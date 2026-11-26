import os  # round 2: source resolved from __file__
import sys
import shutil

def main() -> int:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(script_dir, 'entry.png')
    
    if not os.path.isfile(src):
        print(f'Source not found: {src}', file=sys.stderr)
        return 1
    
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', 'out')
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, 'entry.png')
    
    try:
        shutil.copyfile(src, dst)
    except OSError as e:
        print(f'Copy failed: {e}', file=sys.stderr)
        return 1
    
    try:
        with open(dst, 'rb') as f:
            magic = f.read(8)
    except OSError as e:
        print(f'Read back failed: {e}', file=sys.stderr)
        return 1
    
    if magic != b'\x89PNG\r\n\x1a\n':
        print('Bad PNG magic bytes', file=sys.stderr)
        return 1
    
    size = os.path.getsize(dst)
    print(f'{dst} {size}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
