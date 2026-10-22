"""Run production filesystem/save code beside sentinel legacy installations."""
import os
from pathlib import Path
import subprocess
import tempfile

PORT = Path(__file__).resolve().parents[1]


def main():
    # Reject new literal paths outside the central namespace. Shared mount root
    # creation is intentional; the DSP firmware is loaded by libctru read-only.
    for path in (PORT / 'src').glob('*.c'):
        source = path.read_text()
        assert 'sdmc:/3ds/emerald3ds/' not in source, path
        assert 'sdmc:/3ds/pokeemerald/' not in source, path
    source = (PORT / 'src/3ds_compat.c').read_text()
    save = source[source.index('#define CTR_SAVE_PATH'):source.index('/* ── Entry points')]
    fs = (PORT / 'src/3ds_fs.c').read_text().replace('#include <3ds.h>', '')
    harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/stat.h>
#include "3ds_platform.h"
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef int Result;
#define R_SUCCEEDED(r) ((r) == 0)
static Result romfsInit(void) { return 0; }
static void romfsExit(void) {}
static u8 FLASH_BASE[128 * 1024];
const char *CtrScenario_SavePath(void) { return NULL; }
bool CtrScenario_SaveWrites(void) { return true; }
void CtrLog_Write(CtrLogCategory category, const char *format, ...) {
    (void)category; (void)format;
}
'''
    harness += fs + '\n' + save + r'''
int main(void) {
    assert(CtrFs_Init());
    Port_SaveInit(); /* Must not import or rename either legacy save. */
    assert(Port_SaveIsAvailable());
    for (unsigned i = 0; i < sizeof(FLASH_BASE); ++i) assert(FLASH_BASE[i] == 0xff);
    u8 value = 0x42;
    assert(Port_WriteFlash(12, &value, 1) == 0);
    memset(FLASH_BASE, 0, sizeof(FLASH_BASE));
    Port_SaveInit();
    assert(FLASH_BASE[12] == value && FLASH_BASE[13] == 0xff);
    assert(CtrFs_OpenData("../emerald3ds/emerald3ds.sav", "wb") == NULL);
    assert(CtrFs_OpenData("sdmc:/3ds/emerald3ds/emerald3ds.sav", "wb") == NULL);
    assert(CtrFs_OpenData("/absolute", "wb") == NULL);
    FILE *f = CtrFs_OpenData("settings.txt", "w");
    assert(f && fputs("custom\n", f) >= 0 && fclose(f) == 0);
    CtrFs_Shutdown();
    puts(CTR_DATA_DIR);
    return 0;
}
'''
    for expanded in (False, True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protected = {}
            for app in ('emerald3ds', 'pokeemerald') + (('emerald3ds-custom', 'emerald3ds-custom-stage-b') if expanded else ()):
                folder = root / 'sdmc:' / '3ds' / app
                folder.mkdir(parents=True)
                for name in ('emerald3ds.sav', 'pokeemerald.sav', 'settings.txt',
                             'emerald3ds.clock', 'emerald3ds.clock.bak', 'port.log',
                             'emerald3ds.pak', 'debug.txt'):
                    path = folder / name
                    path.write_bytes(b'legacy must survive: ' + name.encode())
                    protected[path] = path.read_bytes()
            (root / 'romfs:').mkdir()
            (root / 'romfs:' / 'boot.txt').write_text('Emerald3DS RomFS v1\n')
            (root / 'isolation.c').write_text(harness)
            subprocess.run([os.environ.get('CC', 'gcc'), '-std=c99', '-Wall', '-Wextra',
                            '-Werror', *(['-DPORT_EXPANSION'] if expanded else []), '-I' + str(PORT / 'include'), str(root / 'isolation.c'),
                            '-o', str(root / 'isolation')], check=True)
            result = subprocess.run([str(root / 'isolation')], cwd=root, check=True, text=True, capture_output=True)
            for path, original in protected.items():
                assert path.read_bytes() == original, path
            custom = root / result.stdout.strip()
            assert (custom / 'emerald3ds.sav').stat().st_size == 128 * 1024
            assert (custom / 'settings.txt').read_text() == 'custom\n'
    print('PASS production save/filesystem isolation: no migration, isolated writes, traversal rejection, legacy sentinels intact')


if __name__ == '__main__':
    main()
