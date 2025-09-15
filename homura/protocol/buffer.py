from homura.exceptions import *


class Buffer:
    def __init__(self, buffer: bytes):
        self.buffer = buffer
        self.position = 0

    def __len__(self):
        return len(self.buffer)

    def write(self, data: bytes):
        """Writes data to the buffer."""
        self.buffer += data

    def read(self, length: int = None) -> bytes:
        """
        Reads n bytes from the buffer, if the length is None
        then all remaining data from the buffer is sent.
        """

        try:
            if length is None:
                length = len(self.buffer)
                return self.buffer[self.position :]

            return self.buffer[self.position : self.position + length]
        finally:
            self.position += length
