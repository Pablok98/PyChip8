from os.path import join

from PyQt5 import Qt


ROM_PATH = join('roms', 'tank.rom')

"""
Keypad                   Keyboard
+-+-+-+-+                +-+-+-+-+
|1|2|3|C|                |1|2|3|4|
+-+-+-+-+                +-+-+-+-+
|4|5|6|D|                |Q|W|E|R|
+-+-+-+-+       =>       +-+-+-+-+
|7|8|9|E|                |A|S|D|F|
+-+-+-+-+                +-+-+-+-+
|A|0|B|F|                |Z|X|C|V|
+-+-+-+-+                +-+-+-+-+
"""



KEYS = {
    0x0: 'x',
    0x1: '1',
    0x2: '2',
    0x3: '3',
    0x4: 'q',
    0x5: 'w',
    0x6: 'e',
    0x7: 'a',
    0x8: 's',
    0x9: 'd',
    0xA: 'z',
    0xB: 'c',
    0xC: '4',
    0xD: 'r',
    0xE: 'f',
    0xF: 'v',
}