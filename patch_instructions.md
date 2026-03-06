# Instruksi Patching (Versi UI Bypass) untuk libmain.so

Modifikasi sebelumnya yang me-NOP (*No Operation*) proses verifikasi HTTP menyebabkan game *crash* (Force Close) akibat *Null Pointer Dereference*. Server tidak mengembalikan *key* yang valid, sehingga saat game mencoba memproses string/data *key* tersebut ke dalam memori, ia mengakses alamat kosong (Null).

Untuk menyiasatinya, **patch versi ini berfokus langsung pada fungsi *rendering* UI (ImGui)**. Kita tidak lagi mengganggu jalannya pengecekan HTTP (biarkan dia gagal di *background*), tetapi kita meretas logika yang menggambar menu.

Modifikasi berikut telah dilakukan pada fungsi penggambar (*fcn.002bccec*):

1. **Memaksa Skip Menu Login**
   - **Alamat**: `0x002bf308`
   - **Tindakan**: Instruksi asli `cbz w8, 0x2bf650` (yang melompati pembuatan UI Login jika *key* sudah ada) diubah menjadi `b 0x2bf650` (*Unconditional Branch*). Ini berarti *game* tidak akan pernah mencoba menggambar kotak Login, dan langsung melompat ke blok kode yang bertugas menggambar Main Menu.

2. **Memaksa Draw Mod Menu walau Auth Gagal**
   - **Alamat**: `0x002bf66c` dan `0x002bf684`
   - **Tindakan**: Di blok penggambar Main Menu, terdapat pengecekan berlapis (flag dari memori `.bss` pada offset `0x517370` dan `0x5173d8`). Jika flag ini bernilai 0 (karena *login* gagal), instruksi asli akan mengeksekusi branch ke fungsi *exit/return* (`b 0x2cd588` dan `b 0x2cd5b0`). Kita mengubah branch tersebut menjadi `nop` (*No Operation*), sehingga instruksi tetap berjalan dan merender Mod Menu ke layar.

**Cara Penggunaan:**
Jalankan script Python di bawah ini pada file `libmain.so` asli (belum dimodifikasi):
```bash
python3 patch_libmain.py libmain_original.so libmain_patched.so
```
Setelah itu repacking `libmain_patched.so` ke dalam APK Anda.
