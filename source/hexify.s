# Assembly code that is meant to be patched into memory location 0x800945bc of a BeatmaniaIII The Final executable
# which converts the dongle check code to a dongle data dumper. You can compile it using commands like the following:
#
# powerpc-linux-gnu-as -m403 -o hexify.o hexify.s
# powerpc-linux-gnu-ld -e loc_hexify --oformat binary -o hexify.bin hexify.o
# 
# The resulting bin can be loaded into MAME like so, or patched onto a legit binary that was extracted using exe_utils:
#
# load hexify.bin,0x800945bc,0xCC

    .section .text
    .globl loc_hexify

    # Input location is on the stack
    addi      %r10, %r1, 0x38

    # Output location is 0x80505218
    lis       %r11, -0x7FB0
    addi      %r11, %r11, 0x5218

    # Number of bytes output is zero
    li        %r12, 0

loc_hexify:
    cmpwi %r12, 0x90   # 48 byte * 3 sections
    bge loc_finished
    
    # Grab byte into %r3
    lbz %r3, 0(%r10)
    addi %r10, %r10, 1
    
    # Grab top word
    srawi %r4, %r3, 4
    bl sub_hex
    
    # Grab bottom word
    li %r5, 0xF
    and %r4, %r3, %r5
    bl sub_hex
    
    # Add newline if needed, make sure we've output at least ONE character.
    cmpwi %r12, 0x1
    bge might_need_newline
    
    # We haven't output enough bytes so don't bother.
    addi %r12, %r12, 1
    b loc_hexify

might_need_newline:
    # See if we're on a 16 character boundary.
    addi %r12, %r12, 1
    li %r3, 0x0F
    and %r4, %r12, %r3
    cmpwi %r4, 0x1
    
    # We aren't, lets loop again.
    bge loc_hexify
    
    # We are, add a newline
    li %r4, 0x0A
    stb %r4, 0(%r11)
    addi %r11, %r11, 1
    
    # Loop back to start.
    b loc_hexify

sub_hex:
    cmpwi %r4, 0xA
    bge sub_hex_letter
    addi %r4, %r4, 0x30
    b sub_hex_output
    
sub_hex_letter:
    addi %r4, %r4, 0x37

sub_hex_output:
    stb %r4, 0(%r11)
    addi %r11, %r11, 1
    blr

loc_finished:   
    # Done! We need nops to cover up original instructions, we need to
    # cover 0xD0 bytes.
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
    nop
