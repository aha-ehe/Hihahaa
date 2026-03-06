import sys

def patch_file(filename, output_filename):
    with open(filename, 'rb') as f:
        data = bytearray(f.read())

    # We use byte replacements directly.
    # r2 commands used conceptually:
    # 1. 0x2bf308: wa b 0x2bf650 (Branch unconditionally, skip Login Menu entirely)
    # 2. 0x2bf66c: wa nop (Do not exit drawing if auth flag 1 is missing)
    # 3. 0x2bf684: wa nop (Do not exit drawing if auth flag 2 is missing)

    # 0x2bf650 - 0x2bf308 = 0x348
    # b 0x2bf650 -> ARM64 unconditional branch offset encoding:
    # Opcode format: 000101 + imm26
    # 0x348 / 4 = 0xD2
    # 0x140000d2 (Little Endian: d2 00 00 14)

    patches = {
        0x002bf308: b"\xd2\x00\x00\x14", # b 0x2bf650
        0x002bf66c: b"\x1f\x20\x03\xd5", # nop
        0x002bf684: b"\x1f\x20\x03\xd5", # nop
    }

    for offset, new_bytes in patches.items():
        print(f"Applying UI patch at offset {hex(offset)}")
        for i, b in enumerate(new_bytes):
            data[offset + i] = b

    with open(output_filename, 'wb') as f:
        f.write(data)

    print(f"Successfully applied UI bypass patches and saved to {output_filename}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 patch_libmain.py <input.so> <output.so>")
        sys.exit(1)
    patch_file(sys.argv[1], sys.argv[2])
