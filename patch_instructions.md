# Instruksi Patching untuk libmain.so

Modifikasi berikut telah dilakukan pada file `libmain.so` untuk membypass proses verifikasi *key* (HTTP Authentication Loops):

1. **Mem-bypass Check Response HTTP**
   - **Alamat**: `0x002d55d8`
   - **Tindakan**: Instruksi asli `b.ne 0x2d5764` (branch if not equal, yang melompat ke fungsi *exit* atau menggagalkan menu) telah diubah menjadi `nop`. Hal ini akan membuat program selalu melanjutkan eksekusi seolah-olah HTTP *response* valid.

2. **Mem-bypass Pemeriksaan Status Flag (Token/Key)**
   - **Alamat**: `0x002d7cb4` sampai `0x002d7d04` (Multiple `tbnz` instructions)
   - **Tindakan**: Semua instruksi yang melompat ke blok validasi gagal (`0x2d7d3c`, `0x2d7d4c`, dst) diubah menjadi `nop`. Dengan ini, aplikasi tidak akan pernah memanggil fungsi yang menampilkan pesan error "Key Invalid" atau "Expired".

3. **Memaksa Loop Menu Tetap Aktif**
   - **Alamat**: `0x002d7d2c`
   - **Tindakan**: Instruksi akhir `cbz x0, 0x2d55cc` yang bergantung pada kembalian dari validasi HTTP diubah menjadi `b 0x2d55cc` (Unconditional Branch). Ini memaksa *thread* ImGui/Menu untuk terus berjalan (looping kembali ke atas) alih-alih keluar jika *key* ternyata kosong atau salah.

**Catatan Uji Coba (Trial):**
Karena ini adalah *static patching* pada aplikasi yang di-*obfuscate*, mungkin ada kemungkinan aplikasi akan *force close* (crash) jika fungsi lain mendeteksi modifikasi ini. Jika ini terjadi, mohon gunakan Logcat (misalnya via ADB `adb logcat | grep -i fatal`) untuk melihat *stack trace* di alamat mana *crash* terjadi, lalu beri tahu saya.
