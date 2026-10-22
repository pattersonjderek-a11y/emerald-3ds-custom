"""Execute production border, compressed follower and scenic preparation paths.

Synthetic memory/GPU boundaries; these tests do not render on a 3DS.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile
from voxel_runtime_test import function

HERE = Path(__file__).resolve().parent


def source_for(case, tree, port):
    if case == 'border':
        engine = (tree / 'src/fieldmap.c').read_text()
        code = engine[engine.index('#define CAMERA_MAPS_MAX'):engine.index('static bool8 CameraTilesetsMatch(')]
        for signature in ('static inline u16 GetBorderBlockAt(', 'static bool8 CameraTilesetsMatch(',
                          'static unsigned CameraBorderWidth(', 'static unsigned CameraBorderHeight(',
                          'static bool8 CameraBorderDrawable(', 'static void PlaceCameraMap(',
                          'static void AddCameraConnections(', 'static void UpdateCameraMaps(',
                          'const u16 *MapGridGetCameraBorderAt('):
            if signature in engine:
                code += function(engine, signature)
        code += function((port / 'src/voxel/voxel_world.c').read_text(), 'int VoxelWorld_BorderMetatile(')
    elif case == 'follower':
        engine = (tree / 'src/decompress.c').read_text()
        header = (tree / 'include/decompress.h').read_text()
        code = header[header.index('#define MAX_DECOMPRESSION_BUFFER_SIZE'):header.index('enum CompressionMode')]
        code += re.search(r'enum CompressionMode\s*\{.*?\};', header, re.S)[0]
        for signature in ('u32 GetDecompressedDataSize(', 'bool32 IsCompressedData(',
                          'u32 LoadCompressedSpriteSheetByTemplate('):
            code += function(engine, signature)
        sprite = (tree / 'src/sprite.c').read_text()
        code += function(sprite, 'static u32 GetPortSpriteAssetSize(')
        code += function(sprite, 'static u16 LoadSpriteSheetWithOffset(')
        code += function(sprite, 'u16 LoadSpriteSheetByTemplate(')
    else:
        video = (port / 'src/3ds_video.c').read_text()
        code = function(video, 'static bool PrepareBattleWorld(') if 'static bool PrepareBattleWorld(' in video else ''
        begin = video.index('    sBattleWorld = false;', video.index('void CtrVideo_Present(void)'))
        end = video.index('#endif', begin) + len('#endif')
        dispatch = re.search(r'    if \(overworld \|\| (?:battleUpdated|battlePrepared)\)\s+CtrVoxel_AfterSubmit\(start\);\s+else\s+CtrVoxel_Idle\(\);', video)[0]
        code += 'static bool Frame(bool overworld) {\nuint64_t start=0;\n' + video[begin:end] + '\n' + dispatch + '\nreturn sBattleWorld;\n}\n'
    before, after = (HERE / f'visual_{case}_test.c').read_text().split('/* PRODUCTION */')
    return before + code + after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--cc', default='cc')
    parser.add_argument('--port-source', type=Path, default=HERE.parent,
                        help='Port sources to compare; defaults to the canonical overlay')
    parser.add_argument('--case', choices=('border','follower','battle','all'), default='all')
    args = parser.parse_args()
    for case in ('border','follower','battle') if args.case == 'all' else (args.case,):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / 'test.c').write_text(source_for(case, args.tree.resolve(), args.port_source.resolve()))
            subprocess.run([args.cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror',
                            '-Wno-sign-compare','-Wno-unused-parameter','-Wno-unused-function','-fno-pie','-no-pie',
                            '-fsanitize=address,undefined','-fno-omit-frame-pointer',
                            str(path / 'test.c'),'-o',str(path / 'test')],check=True)
            subprocess.run([str(path / 'test')],check=True)
    print('PASS production visual regressions (host ASan/UBSan; no GPU execution)')


if __name__ == '__main__':
    main()
