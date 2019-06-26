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

 * `exe_utils` - Utilities for working with Firebeat EXE files. Run with `--help` to see full options. Can take a `HIKARU.EXE` or `FIREBEAT.EXE` and unpack it to its raw PPC form, as described in the executable format above. This is suitable for decompiling or applying hex edits to change behavior or text. Can also take a raw PPC binary and repack it to a Firebeat EXE file that is accepted on real hardware. Use this to repack binaries that you have edited. Note that PPP binaries are more complex, so when working with them be sure to use the `--ppp` flag. Can also take two Firebeat EXE files and output the diff of their PPC code as a list of patch offsets.

 * `bin_utils` - Utilities for working with raw PPC binaries that have been extracted. Run with `--help` to see full options. Can take two binaries and output the diff between them as a list of patch offsets.

## Patch Offsets

The following are patch offsets that you can apply to a raw PowerPC image that has been extracted. The number on the left of the colon is the hex offset where you should make the change, and the numbers on the right of the colon are the before and after values at that location. To use any of these, obtain an image of the game, copy the Firebeat EXE out of the image, decompress it using the `exe_utils unpack` command, apply the edits using your favorite hex editor, recompress the image using `exe_utils pack` and then replace the Firebeat EXE in the image you obtained the original from.

### Beatmania III Append 7thMIX

#### Skip Dongle Check

 * 8E6C: 48 09 3F 6D -> 38 60 00 00
 * 8EE8: 48 09 40 ED -> 38 60 00 00
 * 9480: 48 09 3C D9 -> 38 60 00 00

### Beatmania III The Final

#### Skip Dongle Check

 * 4490: 48 09 00 3D -> 38 60 00 00
 * 44FC: 48 09 01 CD -> 38 60 00 00
 * 4A70: 48 08 FD DD -> 38 60 00 00

#### Skip FDD Init

If you have one of the many Beatmania III Firebeats where the floppy controller has gone bad, you can use this to skip initializing the floppy. This disables all floppy functionality.

 * 47F8: 48 0C EF 91 -> 38 60 00 00
 * 3FAF4: 4B FF FD 59 -> 38 60 00 00
 * 3FB54: 4B FF FC F9 -> 38 60 00 00

### Keyboard Mania

#### Skip Dongle Check

 * 2C530: 7F C3 F3 78 -> 38 60 00 00

### Keyboard Mania 2ndMIX

#### Skip Dongle Check

 * 51D53: 01 -> 00
 * 51DC3: 02 -> 00
 * 51E17: 03 -> 00
 * 51E4B: 04 -> 00

#### Skip E940 Error

If you have used a donor board from a Pop'n Music or Beatmania III to do a mainboard repair for Keyboard Mania, sometimes it can throw an E940 error after passing all hardware checks. This seems to be an error verifying that the software is running on the right type of Firebeat. This skips this check and allows you to transplant parts between Firebeat boards to make a Keyboard Mania main board.

 * 5A44: 41 82 -> 48 00

### Keyboard Mania 3rdMIX

#### Skip E940 Error

If you have used a donor board from a Pop'n Music or Beatmania III to do a mainboard repair for Keyboard Mania, sometimes it can throw an E940 error after passing all hardware checks. This seems to be an error verifying that the software is running on the right type of Firebeat. This skips this check and allows you to transplant parts between Firebeat boards to make a Keyboard Mania main board.

 * 4F40: 41 82 -> 48 00

### Pop'n Music 4

#### Skip Dongle Check

 * B8EC: 48 00 E8 E1 -> 38 60 00 00
 * B914: 48 00 E7 4D -> 38 60 00 00
 * B924: 48 00 E1 C9 -> 38 60 00 00

### Pop'n Music 5

#### Skip Dongle Check

 * CCFC: 48 01 43 F9 -> 38 60 00 00
 * EFD8: 48 01 21 1D -> 38 60 00 00

### Pop'n Music 6

#### Skip Dongle Check

 * 509B6: FF FF -> 00 00
 * 56498: 48 03 4A 4D -> 38 60 00 00
 * 56520: 48 03 42 E5 -> 38 60 00 00
 * 78A84: 48 01 24 61 -> 38 60 00 00
 * 78ABC: 48 01 1D 49 -> 38 60 00 00
 * 78BD8: 41 82 -> 48 00
 * 8AF4A: FF FF -> 00 00

### Pop'n Music 7

#### Skip Dongle Check

 * 5BEB0: 48 04 20 2D -> 38 60 00 00
 * 5BF54: 48 04 3B 21 -> 38 60 00 00
 * 858E0: 48 01 85 FD -> 38 60 00 00
 * 859FC: 41 82 -> 48 00
 * 8E622: FF FF -> 00 00

### Pop'n Music Mickey Tunes

#### Skip Dongle Check

 * B924: 48 01 26 01 -> 38 60 00 00
 * CD7C: 3D 60 80 10 -> 39 60 00 00
 * CD80: 81 6B 02 94 -> 39 60 00 00
 * DB10: 48 01 04 15 -> 38 60 00 00
 * 1D0FE: FF FF -> 00 00
 * 1E66A: FF Ff -> 00 00

### Pop'n Music Mickey Tunes Update Disk

#### Skip Dongle Check

 * 30524: 48 01 D0 09 -> 38 60 00 00
 * 31E0C: 3D 60 80 15 81 6B 6A 4C -> 39 60 00 00 39 60 00 00
 * 32BB0: 48 01 A9 7D -> 38 60 00 00
 * 43A76: FF FF -> 00 00
 * 4DC72: FF FF -> 00 00
