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

Inside the `utils` directory you will find Python3 code that performs a variety of actions. The target version of Python3 I used was 3.6, but any version newer than this will work as well. The code is organized in a way that will hopefully promote reuse in other areas where it may be useful. On unix-like systems where Python3.6 or greater is installed, you can run these directly. On Windows, run them from the command line that has Python3.6 on the path by prefixing "python3" to the command. Do note that these utilities require the <https://github.com/DragonMinded/arcadeutils> repository be installed before running. The easiest way to do that is `python3 -m pip install -r requirements.txt --upgrade` at the root of this repository.

 * `exe_utils` - Utilities for working with Firebeat EXE files. Run with `--help` to see full options. Note that PPP binaries are more complex, so when working with them be sure to use the `--ppp` flag.
   * `exe_utils unpack` - Can take a `HIKARU.EXE` or `FIREBEAT.EXE` and unpack it to its raw PPC form, as described in the executable format above. This is suitable for decompiling or applying hex edits to change behavior or text.
   * `exe_utils pack` - Can take a raw PPC binary and repack it to a Firebeat EXE file that is accepted on real hardware. Use this to repack binaries that you have edited.
   * `exe_utils diff` - Can take two Firebeat EXE files and output the diff of their PPC code as a list of patch offsets. Use this to generate patch lists like you see below.
   * `exe_utils patch` - Can take a Firebeat EXE file and a list of patch offsets and apply the patches to the EXE file. Use these to apply patch offsets found below to a Firebeat EXE.

 * `dallas_crc` - Simple utility that can replicate an iButton CRC for the laser-etched ROM ID written on the iButton itself.

 * `dongle_dump_utils` - Utilities for crafting dongle dumper executables that run on a Firebeat.
   * `dongle_dump_utils check` - Check an existing executable to see if it is a dumper, and if so what game it is set up to dump.
   * `dongle_dump_utils password` - Update an existing dumper executable to contain the passwords to dump a particular game.
   * `dongle_dump_utils validate` - Perform a simple validation over a reconstructed dongle dump to check it for sanity.

## Patches

The patches that appear in the `patches/` directory are provided for others wishing to fix or change software on their Firebeat-based cabinets. They follow the patch format laid out in bindiff from <https://github.com/DragonMinded/arcadeutils>. The only difference is that the file is first decompressed before file size comparisons and byte modifications are made, and finally the file is recompressed again.
