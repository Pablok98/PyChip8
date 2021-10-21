"""
Hex
A - 10
B - 11
C - 12
D - 13
E - 14
F - 15
"""



"""
Opcode
    NNN: address
    NN: 8-bit constant
    N: 4-bit constant
    X and Y: 4-bit register identifier
    PC : Program Counter
    I : 16bit register (For memory address) (Similar to void pointer);
    VN: One of the 16 available variables. N may be 0 to F (hexadecimal);
"""


# Opcode is two bytes long
opcode = 0x0000
# Chip 8 has a 4k memory
memory = bytearray(4096)

"""
    * 16 x 8-bit general purpose registers (V0 - VF**)
    * 1 x 16-bit index register (I)
    * 1 x 16-bit stack pointer (SP)
    * 1 x 16-bit program counter (PC)
    * 1 x 8-bit delay timer (DT)
    * 1 x 8-bit sound timer (ST)
** VF is a special register - it is used to store the overflow bit
"""
# General purpose registers
v = []
# Index and program counter have a value from 0x000 to 0xFFF
i = 0x000
pc = 0x000
# Timers. Two timer registers that count at 60 Hz. When set above zero they will count down to zero.
dt = 0
st = 0
"""
System memory map
0x000-0x1FF - Chip 8 interpreter (contains font set in emu)
0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F)
0x200-0xFFF - Program ROM and work RAM
"""
"""
The graphics system: The chip 8 has one instruction that draws sprite to the screen. Drawing is 
done in XOR mode and if a pixel is turned off as a result of drawing, the VF register is set.
This is used for collision detection.

The graphics of the Chip 8 are black and white and the screen has a total of 2048 pixels (64 x 32). 
This can easily be implemented using an array that hold the pixel state (1 or 0):
"""
screen = [0 for x in range(64 * 32)]

# Stack is used to remember the current location before a jump is performed
sp = 0
stack = bytearray(16)

# Chip 8 has a HEX based keypad (0x0-0xF)
key = bytearray(16)

# Fetch opcode
memory[pc] = 0xA2
memory[pc + 1] = 0xF0

opcode = memory[pc] << 8 | memory[pc + 1]

# Decode opcode

"""
Because every instruction is 2 bytes long, we need to increment the program counter by two after 
every executed opcode. This is true unless you jump to a certain address in the memory or 
if you call a subroutine (in which case you need to store the program counter in the stack). 
If the next opcode should be skipped, increase the program counter by four.
"""