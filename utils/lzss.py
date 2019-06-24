from typing import Generator, List, Optional


class LZSSDecompressor:
    WINDOW_LENGTH = 0x1000

    FLAG_COPY = 1
    FLAG_BACKREF = 0

    def __init__(self, data: bytes) -> None:
        self.__decompressed: Optional[bytes] = None
        self.data: bytes = data
        self.consumed: int = 0
        self.window: List[int] = [0 for _ in range(self.WINDOW_LENGTH)]
        self.write_pos: int = 0xFEE
        self.read_pos: int = 0x0
        self.read_len: int = 0
        self.flags: int = 0

    def __next_flag(self) -> Optional[int]:
        if self.flags & 0x100 == 0:
            try:
                # Grab flag byte
                self.flags = self.data[self.consumed] | 0xFF00
                self.consumed += 1
            except IndexError:
                # Ran out of flags, we're done
                return None

        flag = self.flags & 0x1
        self.flags >>= 1
        return flag

    def __get_bytes(self) -> Generator[int, None, None]:
        while True:
            # First, handle window copy if its in progress
            while self.read_len > 0:
                # Grab the byte, mirror it to the latest position
                data = self.window[self.read_pos]
                self.window[self.write_pos] = data

                # Bookkeeping
                self.read_len -= 1
                self.read_pos = (self.read_pos + 1) % self.WINDOW_LENGTH
                self.write_pos = (self.write_pos + 1) % self.WINDOW_LENGTH

                # Return the data
                yield data

            # Now, handle the next flag
            flag = self.__next_flag()
            if flag == self.FLAG_COPY:
                # Copy byte to output
                data = self.data[self.consumed]
                self.consumed += 1

                # Copy byte to window buffer
                self.window[self.write_pos] = data
                self.write_pos = (self.write_pos + 1) % self.WINDOW_LENGTH

                # Return the data
                yield data
            elif flag == self.FLAG_BACKREF:
                # Backref into window buffer setup
                try:
                    high = self.data[self.consumed]
                    low = self.data[self.consumed + 1]
                except IndexError:
                    # We're done reading, nothing else to do
                    return

                if (
                    low == 0 and high == 0 and
                    (self.consumed + 2) == len(self.data)
                ):
                    # We have nothing to copy, which means we're done.
                    return

                self.read_len = (low & 0xF) + 3
                self.read_pos = high | ((low << 4) & 0xF00)

                # Consume the bytes
                self.consumed += 2
            else:
                # We don't have anything to decompress, implicitly stop
                # iterating.
                return

    @property
    def decompressed(self) -> bytes:
        if self.__decompressed is None:
            self.__decompressed = bytes(self.__get_bytes())
        return self.__decompressed


class LZSSFakeCompressor:
    WINDOW_LENGTH = 0x1000

    def __init__(self, data: bytes) -> None:
        self.__compressed: Optional[bytes] = None
        self.data: bytes = data
        self.consumed: int = 0

    def __get_bytes(self) -> Generator[bytes, None, None]:
        partial_output = False

        while True:
            # First, output a flag byte
            left = len(self.data) - self.consumed
            if left > 8:
                left = 8

            if left == 0:
                # There's nothing left to consume, return an
                # empty flag byte and stop iterating.
                if partial_output:
                    # We need to output a dummy lookback that's
                    # empty, since we advertised having a lookback.
                    yield b'\x00\x00'
                else:
                    # We had exactly 8 bytes last time, so output a new
                    # flag byte followed by a dummy lookback.
                    yield b'\x00\x00\x00'
                # No more iterating
                return
            elif left == 1:
                partial_output = True
                yield b'\x01'
            elif left == 2:
                partial_output = True
                yield b'\x03'
            elif left == 3:
                partial_output = True
                yield b'\x07'
            elif left == 4:
                partial_output = True
                yield b'\x0F'
            elif left == 5:
                partial_output = True
                yield b'\x1F'
            elif left == 6:
                partial_output = True
                yield b'\x3F'
            elif left == 7:
                partial_output = True
                yield b'\x7F'
            elif left == 8:
                partial_output = False
                yield b'\xFF'

            # Now, output the amount of bytes we need to cheese
            yield self.data[self.consumed:(self.consumed + left)]
            self.consumed += left

    @property
    def compressed(self) -> bytes:
        if self.__compressed is None:
            self.__compressed = b''.join(self.__get_bytes())
        return self.__compressed
