# huskylens.py
import time

class HuskyLens:
    ADDRESS = 0x32

    HEADER1 = 0x55
    HEADER2 = 0xAA
    PROTOCOL_ADDR = 0x11

    CMD_REQUEST_BLOCKS = 0x21
    CMD_RETURN_INFO = 0x29
    CMD_RETURN_BLOCK = 0x2A

    def __init__(self, i2c):
        self.i2c = i2c

    def _make_frame(self, command, data=b""):
        frame = bytearray([
            self.HEADER1,
            self.HEADER2,
            self.PROTOCOL_ADDR,
            len(data),
            command
        ])

        frame.extend(data)

        checksum = sum(frame) & 0xFF
        frame.append(checksum)

        return frame

    def _write_command(self, command, data=b""):
        frame = self._make_frame(command, data)
        self.i2c.writeto(self.ADDRESS, frame)

    def _read_frame(self):
        # First read fixed 5-byte header:
        # 55 AA 11 LEN CMD
        header = self.i2c.readfrom(self.ADDRESS, 5)

        if len(header) != 5:
            return None

        if header[0] != self.HEADER1 or header[1] != self.HEADER2:
            return None

        data_len = header[3]

        # Data + checksum
        tail = self.i2c.readfrom(
            self.ADDRESS,
            data_len + 1
        )

        frame = header + tail

        # checksum check
        if (sum(frame[:-1]) & 0xFF) != frame[-1]:
            return None

        command = frame[4]
        data = frame[5:-1]

        return command, data

    @staticmethod
    def _u16(data, offset):
        return data[offset] | (data[offset + 1] << 8)

    def get_id(self):
        """
        Returns:
            learned ID (1, 2, ...)
            None if no learned object is detected
        """

        self._write_command(self.CMD_REQUEST_BLOCKS)

        time.sleep_ms(20)

        # First response should be RETURN_INFO
        result = self._read_frame()

        if result is None:
            return None

        command, data = result

        if command != self.CMD_RETURN_INFO:
            return None

        if len(data) < 2:
            return None

        count = self._u16(data, 0)

        if count == 0:
            return None

        # Read first detected block
        result = self._read_frame()

        if result is None:
            return None

        command, data = result

        if command != self.CMD_RETURN_BLOCK:
            return None

        if len(data) < 10:
            return None

        object_id = self._u16(data, 8)

        if object_id == 0:
            return None

        return object_id