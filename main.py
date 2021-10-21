import sys
from threading import Thread
from time import sleep
from PyQt5.QtWidgets import QApplication
from chip8 import Chip8
from screen import Screen
import config as c


# Auxiliary hook for printing errors
def hook(type, value, traceback):
    print(type)
    print(traceback)

sys.__excepthook__ = hook


def ch8_loop():
    """
    Emulator loop.
    """
    global cpu
    global screen_
    sleep(1)
    while True:
        cpu.cycle()
        if cpu.draw_flag:
            cpu.draw_flag = False
            screen_.screen = cpu.screen
            screen_.render_screen()
        sleep(0.00051)


if __name__ == "__main__":
    app = QApplication([])
    # Initialize CPU and UI
    cpu = Chip8()
    screen_ = Screen()

    # Connect QT UI signals
    screen_.key_signal.connect(cpu.update_keys)
    screen_.key_press_signal.connect(cpu.key_halt_event)

    # Load ROM to play
    cpu.load_rom(c.ROM_PATH)

    motor_thread = Thread(target=ch8_loop, daemon=True)
    motor_thread.start()
    sys.exit(app.exec())