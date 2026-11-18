# A working news-image-daily entry (Python 3.13, standard library only): its
# image is the entry.png beside this file, and the program copies it to
# /output/entry.png. The gate takes a whole PNG or JPEG of at most 1 MiB and
# 1024 by 1024 pixels, and the judge sees exactly the bytes copied.
#
# After copying, the destination is verified against the source asset (byte
# length and SHA-256 digest), so a truncated or corrupted copy fails loudly
# instead of passing silently.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import hashlib
import os
import shutil

OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
DEST = os.path.join(OUTPUT_DIR, "entry.png")


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


os.makedirs(OUTPUT_DIR, exist_ok=True)
shutil.copyfile(SOURCE, DEST)

if os.path.getsize(DEST) != os.path.getsize(SOURCE) or digest(DEST) != digest(SOURCE):
    raise RuntimeError(f"copy verification failed: {DEST} does not match {SOURCE}")
