import sys

import config as c
from time import sleep
from random import randint
from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QObject
from screen import Screen
import threading

# TODO: Load Font-set


class Chip8(QObject):
    def __init__(self):
        super().__init__()
        self.pc = 0x200
        self.opcode = 0
        self.indx = 0
        self.sp = 0

        self.memory = bytearray(4096)
        self.v = [0] * 16
        self.dt = 0
        self.st = 0
        self.screen = [0 for _ in range(64 * 32)]
        self.stack = bytearray(16)
        self.key = bytearray(16)

        # TODO Clear display
        # TODO Clear Stack
        # TODO Clear registers
        # TODO Clear memory

        # TODO Load fontset

        # TODO Reset timers

        self.draw_flag = False

        self.f_code = {
            0x0: self.call,
            0x1: self.jump_to_address,
            0x2: self.call_subroutine,
            0x3: self.equal_condition,
            0x4: self.not_equal_condition,
            0x5: self.equal_register_condition,
            0x6: self.set_register_value,
            0x7: self.add_to_register,
            0x8: self.register_operation,
            0x9: self.not_equal_register_condition,
            0xA: self.set_index,
            0xB: self.address_jump,
            0xC: self.set_random,
            0xD: self.draw_image,
            0xE: self.key_operation,
            0xF: self.set_misc
        }
        self.pressed_keys = []
        self.key_flag = False
        self.key_store = ''

        self.timer_delay = 0

    def cycle(self):
        # Fetch opcode
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        # print(hex(self.opcode))

        first = (self.opcode & 0xF000) >> 12
        self.f_code[first]()
        self.timer_delay += 1
        if self.timer_delay == 10:
            self.timer_delay = 0
            if self.dt > 0:
                self.dt -= 1
            if self.st > 0:
                if self.st == 1:
                    print("BEEEEEEEEP")
                self.st -= 1

        #print(self.screen)

    def call(self):
        # 0XXX
        case = self.opcode & 0x00FF
        if case == 0x00EE:
            self.end_subroutine()
        elif case == 0x00E0:
            self.clear_screen()
        else:
            self.pc += 2

    def end_subroutine(self):
        # 00EE
        self.pc = (self.stack[self.sp - 1] << 8) + self.stack[self.sp - 2]
        self.pc += 2
        self.sp -= 2

    def clear_screen(self):
        # 00E0
        self.screen = [0 for _ in range(64 * 32)]
        self.pc += 2

    def jump_to_address(self):
        # 1NNN
        self.pc = self.opcode & 0x0FFF

    def call_subroutine(self):
        # 2NNN
        self.stack[self.sp] = self.pc & 0x00FF
        self.stack[self.sp + 1] = (self.pc & 0xFF00) >> 8
        self.sp += 2
        self.pc = self.opcode & 0x0FFF

    def equal_condition(self):
        # 3XNN
        index = (self.opcode & 0x0F00) >> 8
        value = (self.opcode & 0x00FF)
        if self.v[index] == value:
            self.pc += 2
        self.pc += 2

    def not_equal_condition(self):
        # 4XNN
        index = (self.opcode & 0x0F00) >> 8
        value = (self.opcode & 0x00FF)
        if self.v[index] != value:
            self.pc += 2
        self.pc += 2

    def equal_register_condition(self):
        # 5XY0
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        if self.v[index_1] == self.v[index_2]:
            self.pc += 2
        self.pc += 2

    def set_register_value(self):
        # 6XNN
        index = (self.opcode & 0x0F00) >> 8
        self.v[index] = self.opcode & 0x00FF
        self.pc += 2

    def add_to_register(self):
        # 7XNN
        index = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        self.v[index] += value
        # TODO: optimize
        if self.v[index] >= 256:
            self.v[index] -= 256
        self.pc += 2

    def register_operation(self):
        # 8XYN
        # TODO: migrate to python 3.9
        case = self.opcode & 0x000F
        if case == 0x0000:
            self.copy_register_value()
        elif case == 0x0001:
            self.register_or_operation()
        elif case == 0x0002:
            self.register_and_operation()
        elif case == 0x0003:
            self.register_xor_operation()
        elif case == 0x0004:
            self.add_registers_carry()
        elif case == 0x0005:
            self.subtract_registers_carry()
        elif case == 0x0006:
            self.rshift_register()
        elif case == 0x0007:
            self.inv_subtract_registers_carry()
        elif case == 0x000E:
            self.lshift_register()

    def copy_register_value(self):
        # 8XY0
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        self.v[index_1] = self.v[index_2]
        self.pc += 2

    def register_or_operation(self):
        # 8XY1
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        self.v[index_1] = self.v[index_1] | self.v[index_2]
        self.pc += 2

    def register_and_operation(self):
        # 8XY2
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        self.v[index_1] = self.v[index_1] & self.v[index_2]
        self.pc += 2

    def register_xor_operation(self):
        # 8XY3
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        self.v[index_1] = self.v[index_1] ^ self.v[index_2]
        self.pc += 2

    def add_registers_carry(self):
        # 8XY4
        if self.v[(self.opcode & 0x00F0) >> 4] > (
                0xFF - self.v[(self.opcode & 0x0F00) >> 8]):
            self.v[0xF] = 1
        else:
            self.v[0xF] = 0
        # todo: optimize
        self.v[(self.opcode & 0x0F00) >> 8] += self.v[(self.opcode & 0x00F0) >> 4] - (256*self.v[0xF])
        self.pc += 2

    def subtract_registers_carry(self):
        # 8XY5
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        if self.v[index_1] > self.v[index_2]:
            self.v[index_1] -= self.v[index_2]
            self.v[0xF] = 1
        else:
            self.v[index_1] += 256 - self.v[index_2]
            self.v[0xF] = 0
        self.pc += 2

    def rshift_register(self):
        # 8XY6
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        f_bit = self.v[index_1] & 0x1
        self.v[index_2] = self.v[index_1] >> 1
        self.v[0xF] = f_bit
        self.pc += 2

    def inv_subtract_registers_carry(self):
        # 8XY7
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        if self.v[index_2] > self.v[index_1]:
            self.v[index_1] = self.v[index_2] - self.v[index_1]
            self.v[0xF] = 1
        else:
            self.v[index_1] += 256 + self.v[index_2] - self.v[index_2]
            self.v[0xF] = 0
        self.pc += 2

    def lshift_register(self):
        # 8XYE
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        l_bit = (self.v[index_1] & 0x80) >> 8
        self.v[index_2] = self.v[index_1] << 1
        self.v[0xF] = l_bit
        self.pc += 2

    def not_equal_register_condition(self):
        # 9XY0
        index_1 = (self.opcode & 0x0F00) >> 8
        index_2 = (self.opcode & 0x00F0) >> 4
        if self.v[index_1] != self.v[index_2]:
            self.pc += 2
        self.pc += 2

    def set_index(self):
        # AXXX
        self.indx = self.opcode & 0x0FFF
        self.pc += 2

    def address_jump(self):
        # BNNN
        self.pc = (self.opcode & 0x0FFF) + self.v[0]

    def set_random(self):
        # CXNN
        index = (self.opcode & 0x0F00) >> 8
        self.v[index] = randint(0, 255) & (self.opcode & 0x00FF)
        self.pc += 2

    def draw_image(self):
        # DXXX

        """
        Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels.
         Each row of 8 pixels is read as bit-coded starting from memory location I; I value doesn’t
         change after the execution of this instruction. As described above, VF is set to 1 if any
         screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that
         doesn’t happen.
        """
        x = self.v[(self.opcode & 0x0F00) >> 8]
        y = self.v[(self.opcode & 0x00F0) >> 4]
        height = self.opcode & 0x000F
        self.v[0xF] = 0
        for yline in range(height):
            pixel = self.memory[self.indx + yline]
            # pixel = bin(pixel)[2:].zfill(8)
            for xline in range(8):
                if (pixel & (0x80 >> xline)) != 0:
                    try:
                        if self.screen[(x + xline + ((y + yline) * 64))] == 1:
                            self.v[0xF] = 1
                        self.screen[x + xline + ((y + yline) * 64)] ^= 1
                    finally:
                        continue
        # TODO: set drawflag
        self.pc += 2
        self.draw_flag = True

    def update_keys(self, keys):
        self.pressed_keys = keys

    def key_operation(self):
        # EXXX
        case = self.opcode & 0x00FF
        if case == 0x009E:
            self.eq_press_skip()
        elif case == 0x00A1:
            self.neq_press_skip()

    def eq_press_skip(self):
        # EX9E
        index = (self.opcode & 0x0F00) >> 8
        game_key = c.KEYS[self.v[index]]
        if game_key in self.pressed_keys:
            self.pc += 2
        self.pc += 2

    def neq_press_skip(self):
        # EXA1
        index = (self.opcode & 0x0F00) >> 8
        game_key = c.KEYS[self.v[index]]
        if game_key not in self.pressed_keys:
            self.pc += 2
        self.pc += 2

    def set_misc(self):
        # FXXX
        case = self.opcode & 0x00FF
        if case == 0x0007:
            self.store_timer_delay()
        elif case == 0x000A:
            self.key_halt()
        elif case == 0x0015:
            self.set_delay_timer()
        elif case == 0x0018:
            self.set_sound_timer()
        elif case == 0x001E:
            self.index_sum()
        elif case == 0x0029:
            self.index_sprite_loc()
        elif case == 0x0033:
            self.binary_store()
        elif case == 0x0055:
            self.register_dump()
        elif case == 0x0065:
            self.register_load()

    def store_timer_delay(self):
        # FX07
        index = (self.opcode & 0x0F00) >> 8
        self.v[index] = self.dt
        self.pc += 2

    def key_halt_event(self, key_):
        # TODO: optimize to use events
        if not self.key_flag:
            return
        if key_ in c.KEYS.values():
            self.key_flag = False
            self.key_store = key_

    def key_halt(self):
        # FX0A
        index = (self.opcode & 0x0F00) >> 8
        self.pc += 2
        # Code from Chip8Python
        self.key_flag = True
        while self.key_flag:
            sleep(0.001)
        for k, v in c.KEYS.items():
            if v == self.key_store:
                self.v[index] = k

    def set_delay_timer(self):
        # FX15
        index = (self.opcode & 0x0F00) >> 8
        self.dt = self.v[index]
        self.pc += 2

    def set_sound_timer(self):
        # FX18
        index = (self.opcode & 0x0F00) >> 8
        self.st = self.v[index]
        self.pc += 2

    def index_sum(self):
        # FX1E
        index = (self.opcode & 0x0F00) >> 8
        self.indx += self.v[index]
        self.pc += 2

    def index_sprite_loc(self):
        # FX29
        index = (self.opcode & 0x0F00) >> 8
        self.indx = self.v[index] * 5
        self.pc += 2

    def binary_store(self):
        # FX33
        self.memory[self.indx] = self.v[(self.opcode & 0x0F00) >> 8] // 100
        self.memory[self.indx + 1] = (self.v[(self.opcode & 0x0F00) >> 8] // 10) % 10
        self.memory[self.indx] = (self.v[(self.opcode & 0x0F00) >> 8] % 100) % 10
        self.pc += 2

    def register_dump(self):
        # FX55
        index = (self.opcode & 0x0F00) >> 8
        for ind in range(index + 1):
            self.memory[self.indx + ind] = self.v[ind]
        self.pc += 2

    def register_load(self):
        # FX65
        index = (self.opcode & 0x0F00) >> 8
        for ind in range(index + 1):
            self.v[ind] = self.memory[self.indx + ind]
        self.pc += 2

    def load_rom(self, path):
        with open(path, 'rb') as rom:
            for i, byte_ in enumerate(rom.read()):
                self.memory[i + 512] = byte_


