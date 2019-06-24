import struct
from lzss import LZSSDecompressor, LZSSFakeCompressor


class FirebeatExe:

    @staticmethod
    def exe_to_raw(data: bytes) -> bytes:
        size = struct.unpack("<I", data[:4])[0]
        lz = LZSSDecompressor(data[4:])
        decompressed = lz.decompressed

        if len(decompressed) != size:
            raise Exception("Decompression error!")

        return decompressed

    @staticmethod
    def raw_to_exe(data: bytes) -> bytes:
        header = struct.pack("<I", len(data))
        lz = LZSSFakeCompressor(data)
        return header + lz.compressed
