# Security Dongle Theory of Operation and Dumping

All firebeat games use a Dallas DS1991 iButton connected to the firebeat through
a DB9 interface as the protection against piracy and as a factory service switch.
The DS1991 is a small 1-wire non-volatile memory device with three 48-byte
enclaves that can hold any data. Each enclave is password-protected by an 8-byte
key and identified with an 8-byte ID. In order to read a secure enclave you must
provide the correct password. If you don't, the dongle will appear to return
memory but it will be random data. It is not clear whether the data returned is
an XOR with the key provided or if the DS1991 generates actual random data when
the key is wrong. If it is an XOR then we can use knowledge of what should appear
in the enclaves as a way of brute-forcing the password, but this has not been
researched. In practice it is not necessary as all known dongle variant passwords
are extracted.

In order to access the security key without forcing the game to be initialized
and locked to a particular token, each firebeat executable must include the IDs
and passwords for the three secure enclaves. In practice, they are easy to find
in the executable as they tend to appear next to factory mode selection strings.
From examining various games and seeing how they use tokens it appears that
firebeat games use a similar mechanism for securing themselves with a dongle.
Games will read all three enclaves using three supplied IDs and passwords
embedded in the binary.

The first enclave is the unique serial number for the copy of the game and
starts with the 3-letter code for the game (C01 in the case of BeatmaniaIII The
Final) and is followed by six digits. The game will verify that the 3-letter
code is a match and reject dongles that do not match, and will display the
9-digit serial on the boot-up and attract screen. Almost every game will use
the fourth digit as a region selection switch, comparing it to the cabinet
ID register. Normally, digits 1, 3 and 7 specify Japan region, 2 and 4 specify
overseas, and 0 and 9 are reserved. Some games use 9 as a rental code, some
use 0. It does not appear to validate the rest of the digits so any valid
displayable ascii string is technically a correct dongle as long as the first
3 digits match the game code and the fourth digit is correct for the hardware
you are running on. The rest of the enclave appears to be filled with ascii
space characters.

The second enclave appears to be completely ignored in most games aside from
verifying that the data itself can be transferred. It appears to be filled
entirely with ascii space characters. For the few games that do use this
enclave (Pop'n Music Mickey Tunes, Animelo 1 and 2) this includes additional
license information. On KeyboardMania 2ndMIX this enclave appears to be filled
with random data that matches on both Japan and overseas regions so it is possible
that the enclave password is incorrect or whoever programmed the dongles didn't
initialize the second enclave properly.

The third enclave is the service mode enclave and is normally all ascii
space characters on a consumer dongle. Various games recognize various
alternate strings placed into this enclave which enable different modes
of the game. Some games have recognition for event mode, manufacturer mode,
service mode, debug mode, easy mode, and others. The game will compare the
full enclave data against a list of known strings and enable various modes
depending on which one matches, defaulting to a standard game mode if there
is no match.

There is an additional 8 byte ROM ID that is unique and read-only for each
DS1991 button. This is completely unused in firebeat games. All games skip
reading the ID and make no use of it. However, when dumping a dongle it should
be included in the dump at the end of the file. Fortunately the ROM ID is
laser engraved on the iButton itself. To retrieve the ROM ID, remove the iButton
from the DB9 enclosure and flip it over. You'll notice a 2 digit hex number on
the left, a 2 digit hex number on the right and a 12 digit hex number below
both of them. The left number is the ROM ID CRC, the right is the product code
(always 02) and the bottom is the unique serial number. This should be transcribed
by first noting down the CRC, then the 12 digit serial, and finally the product
code (02). Then the bytes should be reversed. This can be checked by using the
`dallas_crc` utility by providing the hex codes for the first seven bytes (after
reversing them), and you should get a hex CRC value that matches the 8th byte.

## Dumping Theory

In order to dump the secure enclave of a security iButton, you must know the
correct ID and password for that enclave and have hardware capable of interfacing
with the iButton itself. It just so happens that a firebeat has compatible
hardware for interfacing with an iButton, and the ID and password can be mined out
of the decompressed executable for each game. Looking at the bootup sequence
for BeatmaniaIII The Final, the game first sets up a multithreaded environment,
then kicks off a watchdog thread and then kicks off the main game thread. The
main game thread performs some basic C runtime initialization and then jumps
to the hardware init and check code. The check code first prints the checklist
of all areas to verify and then starts by initializing the IO. Then it reads
and verifies the dongle before moving on to the rest of the checks. The dongle
read code first zeros out the serial number global, then performs a secure
enclave read for each of the three enclaves, and finally verifies the data in
those enclaves. The first, as documented above, is verified to start with "C01"
and then the 9 digit serial number is copied to the serial number global. The
second enclave is ignored, and the third enclave is compared against manufacture
mode and service mode strings and if found, a manufacture mode global is set.
Finally, the function returns with a return code that signifies that either the
dongle was not presesnt, the dongle was present but the serial was bad, or that
everything was good and to continue booting. The serial global is displayed
on the startup screen below the game model number and it continues booting.

Two things can be gained from this understanding. First, that the game does
not seem to use the serial number in any way aside from verifying that it is
in the correct range and matches the cabinet info register's region. This means
that it is trivial to bypass the security by simply skipping the dongle read
and jumping directly to the "OK" response. Second, if you have the correct IDs
and passwords for a dongle in the game's code, it will read all 3 48-byte
enclaves to a buffer on the stack. This means if you were to modify the serial
number copy and check code to instead copy the hex values of all 3 enclaves to
the serial number global before returning you would have a working dongle dump
utility. This is precisely what the dongledumper.patch modifications achieve.
The meat of the change is replacing the check and copy with a hex conversion loop
and resizing the stack for the game's printf implementation so that the very long
string doesn't blow the stack and cause an exception. The rest of the
modifications are there to make the output on the screen prettier and to halt the
game from continuing once it does print the dongle while still petting the
watchdog. To read the dongle for another game, one must replace the ID and
password strings with the correct ID and password pairs from that game itself.
This can be accomplished using the `dongle_dump_utils` utility which already
contains all of the known passwords. Aside from that, everything works as desired.

Once you have all three enclaves output and have noted the ROM ID from the
iButton itself, you can reconstruct a dongle file for use with MAME or to rewrite
a new dongle if you have the capability. For MAME, the dongle file should look
like a raw dump of the entire iButton from the perspective of the iButton
internals. That means the first ID (8 bytes), then the first password (8 bytes)
and then the first enclave (48 bytes). Concatenate those, and do the same for
the second ID, password and enclave, followed by the third. Finally, the 8
byte ROM ID should follow all 3 enclaves. If done correctly, the resulting file
should be exactly 200 bytes long. If you have an empty iButton you can program
the three enclaves by using the ID and passwords followed by a copy of the data
from another dongle or hand crafted data if you so desire. You can also verify
that your dump looks correct using the `dongle_dump_utils` utlity.
