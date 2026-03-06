# Reverse Engineering Report: `libmain.so` (Magic Chess Go Go Mod Menu)

## 1. File Overview
- **Name**: `libmain.so`
- **Architecture**: ARM64 (AArch64)
- **Format**: ELF 64-bit LSB shared object
- **Compiler/Linker**: LLD 14.0.1 Android (Clang 7.0.2 / LLVM)
- **Dynamic Linking**: Yes (Dynamically Linked, Stripped)
- **Protection**: The file is **not packed** with standard packers like UPX (sections `.text`, `.rodata`, `.data` are intact). However, the logic is heavily obfuscated. `JNI_OnLoad` contains a decryption routine that calculates strings dynamically before passing them to `dlopen()` and `dlsym()`. This means the actual mod menu logic might be loading another hidden library or resolving hidden API functions at runtime to evade static detection.

## 2. Key Components Found

### 2.1 Networking & Authentication (Key Verification)
The binary contains significant networking logic to verify the user's "key" and communicate with an external server. It statically links **libcurl** and **OpenSSL**:
- **HTTP/HTTPS References**: Extensive strings relating to HTTP headers, proxy connections, and HTTP/1.1 requests.
  - Hardcoded URL related to cookies: `https://curl.haxx.se/docs/http-cookies.html`
  - Multiple functions constructed to parse and send HTTP requests (e.g., `fcn.000c2788` which contains `http_proxy` strings and is called by the main thread).
- **Authentication/SSL**:
  - Contains full OpenSSL error strings like `could not load ASN1 client certificate, OpenSSL error %s, (no key found, wrong pass phrase, or wrong file format?)`.
  - Keys, certificates, and tokens are validated using functions like `SSL_CTX_use_RSAPrivateKey`, `EVP_PKEY_verify`, `PEM_read_bio_PrivateKey`.
  - A potential "Token" structure used: `setct-CapTokenTBS`, `setct-AuthTokenTBS`.

### 2.2 Mod Menu GUI (ImGui)
The binary implements an overlay menu.
- Strings explicitly mention **ImGui** (e.g., `https://github.com/ocornut/imgui/blob/master/docs/FAQ.md#qa-usage`).
- Internal UI inputs are processed via strings like `Keypad0`, `Keypad1`, `KeypadMultiply`, `KeypadEnter`, etc., showing that the mod menu responds to touch or external controller inputs to toggle cheats.

### 2.3 `JNI_OnLoad` Analysis (Entry Point)
`JNI_OnLoad` (located at `0x002e9d3c`) is the only exported function and acts as the entry point when the Android application loads this `.so` file.
- **Obfuscation**: Before calling any standard Android APIs, it executes a loop (at `0x2ea164`) that XORs and adds bytes to decrypt a string dynamically in memory.
- **Dynamic Loading**: It calls `dlopen()` on this decrypted string, followed by `dlsym()` to locate specific functions. This implies the main payload or validation functions are hidden and loaded on the fly to prevent easy static patching.
- **Thread Creation**: The initialization routines eventually spawn multiple background threads using `pthread_create`, likely used for the HTTP keep-alive, key verification loop, and drawing the ImGui overlay.

## 3. URLs and External Services
- `android.googlesource.com/toolchain/clang` (Compiler artifact)
- `github.com/ocornut/imgui/...` (ImGui source/FAQ reference)
- The actual API endpoint used for key validation is dynamically constructed or encrypted, as it did not appear in plain text during static analysis. The network requests are handled over HTTPS using `libcurl`.

## 4. Recommendations for Next Steps (Patching/Taking Over)
To bypass the key verification or take over this mod menu, the following approaches are recommended:
   - Hook `curl_easy_perform` or `SSL_write`/`SSL_read` to intercept the HTTPS request sending the "key" to the server. You can intercept the response and force it to return a "success/valid" status code.
2. **Static Patching**:
   - Since the key validation likely relies on an HTTP response, you can find the function evaluating the HTTP response code (usually comparing `w0` against `200` or a specific JSON body) and patch the branch instruction (e.g., changing `B.NE` to `B.EQ` or `NOP`) to always open the menu regardless of the server's response.
