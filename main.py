#!/usr/bin/env python3
"""KORVATH poster entrypoint.

Copies the poster image (entry.png, shipped next to this file) to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output) and validates it the
way the gate does: whole PNG, at most 1,048,576 bytes, 1024x1024.

Stdlib only — the sandbox may not have PIL.
"""
import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
WANT_W, WANT_H = 1024, 1024
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print("ERROR:", msg, file=sys.stderr)
    sys.exit(1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        fail("entry.png not found next to main.py")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)

    with open(dst, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        fail("entry.png is %d bytes, over the 1,048,576 limit" % len(data))
    if data[:8] != PNG_SIG:
        fail("entry.png is not a PNG (bad signature)")
    if len(data) < 24:
        fail("entry.png is too short to hold an IHDR")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (WANT_W, WANT_H):
        fail("entry.png is %dx%d, expected 1024x1024" % (width, height))
    print("wrote %s (%d bytes, %dx%d)" % (dst, len(data), width, height))


if __name__ == "__main__":
    main()
