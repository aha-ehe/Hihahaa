import sys

def patch_file(filename, output_filename):
    with open(filename, 'rb') as f:
        data = bytearray(f.read())

    # Patches at offsets based on r2 analysis
    # Note: File offsets in ELF might differ from virtual addresses if not mapped 1:1.
    # Let's calculate file offsets.
    # .text section starts at vaddr 0xbb6b0, offset 0xbb6b0 (it's a 1:1 mapping for this file's text section!)

    patches = {
        0x002d55d8: b"\x1f\x20\x03\xd5", # nop
        0x002d7cb4: b"\x1f\x20\x03\xd5", # nop
        0x002d7cbc: b"\x1f\x20\x03\xd5", # nop
        0x002d7cc4: b"\x1f\x20\x03\xd5", # nop
        0x002d7ccc: b"\x1f\x20\x03\xd5", # nop
        0x002d7cd4: b"\x1f\x20\x03\xd5", # nop
        0x002d7cdc: b"\x1f\x20\x03\xd5", # nop
        0x002d7ce4: b"\x1f\x20\x03\xd5", # nop
        0x002d7cec: b"\x1f\x20\x03\xd5", # nop
        0x002d7cf4: b"\x1f\x20\x03\xd5", # nop
        0x002d7cfc: b"\x1f\x20\x03\xd5", # nop
        0x002d7d04: b"\x1f\x20\x03\xd5", # nop
        0x002d7d2c: b"\x68\xf6\xff\x17", # b 0x2d55cc
    }

    for offset, new_bytes in patches.items():
        print(f"Applying patch at offset {hex(offset)}")
        for i, b in enumerate(new_bytes):
            data[offset + i] = b

    with open(output_filename, 'wb') as f:
        f.write(data)

    print(f"Successfully patched and saved to {output_filename}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 patch_libmain.py <input.so> <output.so>")
        sys.exit(1)
    patch_file(sys.argv[1], sys.argv[2])
