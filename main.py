import os
import shutil

def main():
    src = "entry.png"
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, dst)
    with open(dst, "rb") as f:
        header = f.read(8)
    if header != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Copied image is not a valid PNG")
    size = os.path.getsize(dst)
    print(dst)
    print(size)

if __name__ == "__main__":
    main()
