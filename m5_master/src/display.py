# display.py
from machine import Pin, SPI
import framebuf
import time

class Display:
    WIDTH = 135
    HEIGHT = 240

    # M5StickC PLUS2 LCD pins
    PIN_MOSI = 15
    PIN_CLK  = 13
    PIN_DC   = 14
    PIN_RST  = 12
    PIN_CS   = 5
    PIN_BL   = 27

    # ST7789 commands
    SWRESET = 0x01
    SLPOUT  = 0x11
    NORON   = 0x13
    INVOFF  = 0x20
    INVON   = 0x21
    DISPON  = 0x29
    CASET   = 0x2A
    RASET   = 0x2B
    RAMWR   = 0x2C
    MADCTL  = 0x36
    COLMOD  = 0x3A

    def __init__(self):
        self.spi = SPI(
            1,
            baudrate=20_000_000,
            polarity=0,
            phase=0,
            sck=Pin(self.PIN_CLK),
            mosi=Pin(self.PIN_MOSI),
        )

        self.dc = Pin(self.PIN_DC, Pin.OUT)
        self.rst = Pin(self.PIN_RST, Pin.OUT)
        self.cs = Pin(self.PIN_CS, Pin.OUT)
        self.bl = Pin(self.PIN_BL, Pin.OUT)

        self.cs.value(1)
        self.bl.value(1)

        # 16-bit RGB565 framebuffer
        self.buffer = bytearray(self.WIDTH * self.HEIGHT * 2)
        self.fb = framebuf.FrameBuffer(
            self.buffer,
            self.WIDTH,
            self.HEIGHT,
            framebuf.RGB565,
        )

        self._init_lcd()
        self.clear()
        self.show()

    def _write_cmd(self, cmd, data=None):
        self.cs.value(0)

        self.dc.value(0)
        self.spi.write(bytes([cmd]))

        if data is not None:
            self.dc.value(1)
            self.spi.write(data)

        self.cs.value(1)

    def _reset(self):
        self.rst.value(1)
        time.sleep_ms(50)
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(150)

    def _init_lcd(self):
        self._reset()

        self._write_cmd(self.SWRESET)
        time.sleep_ms(150)

        self._write_cmd(self.SLPOUT)
        time.sleep_ms(120)

        # RGB565
        self._write_cmd(self.COLMOD, b"\x55")
        time.sleep_ms(10)

        # Orientation
        self._write_cmd(self.MADCTL, b"\x00")

        # Color inversion is normally used on this panel
        self._write_cmd(self.INVON)

        self._write_cmd(self.NORON)
        time.sleep_ms(10)

        self._write_cmd(self.DISPON)
        time.sleep_ms(100)

    def _set_window(self, x0, y0, x1, y1):
        # ST7789 135x240 panels use an internal RAM larger
        # than the visible area.
        #
        # M5StickC PLUS2 portrait offset:
        x_offset = 52
        y_offset = 40

        x0 += x_offset
        x1 += x_offset
        y0 += y_offset
        y1 += y_offset

        self._write_cmd(
            self.CASET,
            bytes([
                x0 >> 8, x0 & 0xff,
                x1 >> 8, x1 & 0xff,
            ]),
        )

        self._write_cmd(
            self.RASET,
            bytes([
                y0 >> 8, y0 & 0xff,
                y1 >> 8, y1 & 0xff,
            ]),
        )

        self._write_cmd(self.RAMWR)

    def clear(self):
        self.fb.fill(0)

    def text(self, text, x=0, y=0):
        # framebuf standard 8x8 font
        # white on black
        self.fb.text(text, x, y, 0xffff)

    def text2x(self, text, x=0, y=0):
        # 1文字ずつ一時バッファに描いて、2倍に拡大して転送する
        char_buf = bytearray(8 * 8 * 2)
        char_fb = framebuf.FrameBuffer(
            char_buf,
            8,
            8,
            framebuf.RGB565
        )

        for ch in text:
            char_fb.fill(0)
            char_fb.text(ch, 0, 0, 0xffff)

            for py in range(8):
                for px in range(8):
                    color = char_fb.pixel(px, py)

                    if color:
                        dx = x + px * 2
                        dy = y + py * 2

                        self.fb.pixel(dx,     dy,     color)
                        self.fb.pixel(dx + 1, dy,     color)
                        self.fb.pixel(dx,     dy + 1, color)
                        self.fb.pixel(dx + 1, dy + 1, color)
            x += 16

    def show(self):
        self._set_window(
            0,
            0,
            self.WIDTH - 1,
            self.HEIGHT - 1,
        )

        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(self.buffer)
        self.cs.value(1)

    def backlight(self, on=True):
        self.bl.value(1 if on else 0)
