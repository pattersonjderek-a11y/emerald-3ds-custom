"""ASan/UBSan execution of production keyed resolvers and native adapters."""
import argparse
from pathlib import Path
import subprocess
import tempfile
from voxel_runtime_test import function

HERE = Path(__file__).resolve().parent


def compile_run(cc, tree, source):
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary)
        (path / 'test.c').write_text(source)
        subprocess.run([cc, '-std=gnu11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                        '-Wno-unused-parameter', '-Wno-sign-compare', '-Wno-pointer-to-int-cast', '-fno-pie', '-no-pie',
                        '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                        '-iquote', str(tree / 'include'), str(path / 'test.c'),
                        str(tree / 'src/custom_run_config.c'), str(tree / 'src/custom_random_core.c'),
                        '-o', str(path / 'test')], check=True)
        subprocess.run([str(path / 'test')], check=True)


def native(tree):
    source = (HERE / 'custom_random_fixture.h').read_text()
    actual = (tree / 'src/custom_random.c').read_text()
    source += actual[actual.index('static struct CRPoolEntry'):actual.rindex('#endif')]
    run = (tree / 'src/custom_run.c').read_text()
    for signature in ('static uint32_t TrainerId(void)', 'enum CRStatus CustomRun_Read(', 'bool CustomRun_CanPlay('):
        source += function(run, signature)
    battle = (tree / 'src/battle_setup.c').read_text()
    source += function(battle, 'void CreateNPCTrainerPartyFromTrainer(struct Pokemon *party,')
    source += function(battle, 'static void CreateNPCTrainerParty(struct Pokemon *party, u16 trainerNum)\n{')
    source += function((tree / 'src/starter_choose.c').read_text(), 'u16 GetStarterPokemon(u16 chosenStarterId)')
    source += function(battle, 'static void CB2_GiveStarter(void)\n{')
    source += function((tree / 'src/wild_encounter.c').read_text(), 'u16 GetCurrentMapWildMonHeaderId(void)')
    source += function((tree / 'src/trainer_pools.c').read_text(), 'static u32 GetPoolSeed(const struct Trainer *trainer)\n{')
    source += (HERE / 'custom_random_native_test.c').read_text()
    return source


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tree', type=Path, required=True)
    p.add_argument('--cc', default='cc')
    args = p.parse_args()
    tree = args.tree.resolve()
    compile_run(args.cc, tree, (HERE / 'custom_random_core_test.c').read_text())
    compile_run(args.cc, tree, native(tree))
    print('Production core randomizer PASS (ASan + UBSan; synthetic engine state)')


if __name__ == '__main__':
    main()
