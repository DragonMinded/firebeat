# Assembly code that is meant to be patched into memory location 0x8007ec5c of a BeatmaniaIII The Final executable
# which converts the test screen DIPswitch code into a register write for experimenting with HW. Also, make sure to
# patch location 0x80003b60 with the value 0x60 0x00 0x00 0x00 (NOP) to stop the WD thread from overwriting the
# LEDs (this is a bug even in the test mode for a standard BMIII image, but we want to see what value we're writing
# to the register).
#
# powerpc-linux-gnu-as -m403 -o register.o register.s
# powerpc-linux-gnu-ld -e loc_register --oformat binary -o register.bin register.o
# 
# The resulting bin can be loaded into MAME like so, or patched onto a legit binary that was extracted using exe_utils:
#
# load hexify.bin,0x8007ec5c,0x4C

    .section .text
    .globl loc_register

loc_register:
    # Input location is R3, from previous code. 0x7D000500 is the register we are writing.
    lis       %r12, 0x7D00
    stb       %r3, 0x0500(%r12)

    # Don't exit the loop, we will ignore the service/test prompt and spin forever.
    li        %r3, 0x00000001

loc_finished:   
    # Done! We need nops to cover up original instructions, we need to
    # cover 0x4C bytes.
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
