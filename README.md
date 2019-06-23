# Firebeat Info and Utilities
This repo serves as a centralized location for me to document and upload utilities for working with Konami Firebeat images.

## System Info

Konami Firebeat is a notoriously flaky stack that runs several older rhythm games. For information on the hardware itself, please see [gamerepair.info](https://gamerepair.info/hardware/5_firebeat). Every single firebeat version boots from an onboard BIOS and then transfers control to an executable found on the primary CD. As far as I know, the format of the executable is always the same, although the name of the executable changes depending on the game you are booting.

## Executable Format

The first four bytes of the executable should be interpreted as a little endian unsigned integer. This is the size of the executable once it has been decompressed in main RAM. The rest of the file is a LZ77-compressed binary. If extracted correctly, it should exactly equal the size specified in the first four bytes. The name of the executable is as dictated below:

 * Beatmania III - `HIKARU.EXE`
 * KeyboardMania - `FIREBEAT.EXE`
 * Pop'n Music - `FIREBEAT.EXE`
 * ParaParaParadise - `HIKARU.EXE`

You can use MAME to decompress images if you are in a pinch and do not have working LZ77 tools. Boot the game image that you wish to decompress the executable from, wait until it boots past the BIOS and starts running through hardware checks, and then dump the main RAM starting at address `0x00` and ending at the size specified in the first four bytes of the EXE as found on disk. This raw image can be made back into an EXE again by first dummy compressing (insert an `0xFF` byte before every 8 byte chunk in the raw image) and re-appending the executable size. If replaced on disk, both MAME and real hardware will happily boot this executable.

## Working with Disk Images

Images can be ripped and burned again using your favorite image reading/writing software. However, to modify an image (such as to replace the EXE with a new one), you should use UltraISO. I have had success modifying images ripped using ImgBurn, using UltraISO to replace the EXE and then burning the updated image with ImgBurn. Your results may vary, but IIRC the sector size for Firebeat images is nonstandard so you need a program that respects that when updating images. You can test that you've created an updated image using MAME. If you start mame with the `-debug` flag, you can choose an ISO to use in place of any disk. An example mame command line to test Beatmania III The Final modifications is `mame64 -window -debug bm3final`