# Firebeat Info and Utilities
This repo serves as a centralized location for me to document and upload utilities for working with Konami Firebeat images.

## System Info

Konami Firebeat is a notoriously flaky stack that runs several older rhythm games. For information on the hardware itself, please see [gamerepair.info](https://gamerepair.info/hardware/5_firebeat). Every single firebeat version boots from an onboard BIOS and then transfers control to an executable found on the primary CD. The program code both in BIOS and on disk is PowerPC and is executed by the 403GCX chip. The name of the executable is as dictated below:

 * Beatmania III - `HIKARU.EXE`
 * KeyboardMania - `FIREBEAT.EXE` or `HIKARU.EXE` depending on the mix.
 * Pop'n Music - `FIREBEAT.EXE`
 * ParaParaParadise - `HIKARU.EXE`

## Executable Format

### ParaParaParadise

The EXE fomat for PPP is a bit more complex than for the other three game series. The first 8 bytes of the file should equal the binary sequence `21 3a 45 58 45 3a 30 30`. The next four bytes should be interpreted as a big-endian unsigned integer, indicating how large the compressed LZSS data contained in the EXE is. The next four bytes should be interpreted as a big-endian unsigned integer, indicating the load address of the executable. This is observed to be `0x80000000` (a mirror of address `0x0`) in practice and is the location that the BIOS for the other game series implicitly loads the executable to. Then, there are 16 bytes of zeros. Next, a simple executable, as described in the "All Others" section below (as in, four bytes indicating the uncompressed size followed by LZSS-compressed data). Finally, the last 8 bytes of the file should equal the binary sequence `21 3a 45 58 45 3a 30 30` (identical to the header). If you strip away the first 32 bytes and the last 8 bytes, this image becomes identical to the other game series, so this is likely a simple header added for flexibility in load address.

### All Others

The first four bytes of the executable should be interpreted as a little endian unsigned integer. This is the size of the executable once it has been decompressed in main RAM. The rest of the file is a LZSS-compressed PowerPC binary. If extracted correctly, its length should exactly equal the size specified in the first four bytes. The last four bytes of the decompressed executable is the entrypoint. It should be a branch instruction (`0x4BF0xxxx`) causing the BIOS to jump to the actual start of the binary. In practice, the four preceding bytes are a second entrypoint but seems to always jump to the same address.

You can use MAME to decompress images if you are in a pinch and do not have working LZSS tools. Boot the game image that you wish to decompress the executable from in debug mode, wait until it boots past the BIOS and starts running through game-specific hardware checks, and then dump the main RAM starting at address `0x0` and ending at the size specified in the first four bytes of the EXE as found on disk. An example MAME debugger command to dump Beatmania III The Final's uncompressed executable is `save hikaru.bin, 0x0, 0x100000`. This raw image can be made back into an EXE again by first dummy compressing (insert an `0xFF` byte before every 8 byte chunk in the raw image) and then re-appending the executable size. If replaced on disk, both MAME and real hardware will happily boot this executable.

## Working with Disk Images

Images can be ripped and burned again using your favorite image reading/writing software. However, to modify an image (such as to replace the EXE with a new one), you should use UltraISO. I have had success modifying images ripped using ImgBurn, using UltraISO to replace the EXE and then burning the updated image with ImgBurn. Your results may vary, but IIRC the sector size for Firebeat images is nonstandard so you need a program that respects that when updating images. You can test that you've created a working updated image using MAME. If you start MAME with the `-debug` flag, you can choose an ISO to use in place of any disk. An example MAME command line to test Beatmania III The Final modifications is `mame64 -window -debug bm3final`

## Utilities

Inside the `utils` directory you will find Python3 code that performs a variety of actions. The target version of Python3 I used was 3.6, but any version newer than this will work as well. The code is organized in a way that will hopefully promote reuse in other areas where it may be useful.

 * `exe_utils` - Utilities for packing and unpacking Firebeat EXE files. Run with `--help` to see full options. Can take a `HIKARU.EXE` or `FIREBEAT.EXE` and unpack it to its raw PPC form, as described in the executable format above. This is suitable for decompiling or applying hex edits to change behavior or text. Can also take a raw PPC binary and repack it to a Firebeat EXE file that is accepted on real hardware. Use this to repack binaries that you have edited. Note that PPP binaries are more complex, so when working with them be sure to use the `--ppp` flag.

## Patch Offsets

The following are patch offsets that you can apply to a raw PowerPC image that has been extracted. The number on the left of the colon is the hex offset where you should make the change, and the numbers on the right of the colon are the before and after values at that location. To use any of these, obtain an image of the game, copy the Firebeat EXE out of the image, decompress it using the `exe_utils unpack` command, apply the edits using your favorite hex editor, recompress the image using `exe_utils pack` and then replace the Firebeat EXE in the image you obtained the original from.

### Beatmania III Append 7thMIX

#### Skip Dongle Check

 * 8E6C: 48 09 3F 6D -> 38 60 00 00
 * 8EE8: 48 09 40 ED -> 38 60 00 00
 * 9480: 48 09 3C D9 -> 38 60 00 00
