import struct
from typing_extensions import Final

from lzss import LZSSDecompressor, LZSSFakeCompressor


class FirebeatExe:

    PPP_LOAD_OFFSET: Final[int] = 0x80000000
    PPP_IMAGE_HEADER: Final[bytes] = b"\x21\x3a\x45\x58\x45\x3a\x30\x30"
    PPP_IMAGE_FOOTER: Final[bytes] = b"\x21\x3a\x45\x58\x45\x3a\x30\x30"

    @staticmethod
    def __simple_exe_to_raw(data: bytes) -> bytes:
        size = struct.unpack("<I", data[:4])[0]
        lz = LZSSDecompressor(data[4:])
        decompressed = lz.decompressed

        if len(decompressed) != size:
            raise Exception("Decompression error!")

        return decompressed

    @staticmethod
    def __ppp_exe_to_raw(data: bytes) -> bytes:
        # First check header and footer
        if data[:8] != FirebeatExe.PPP_IMAGE_HEADER:
            raise Exception("Invalid header!")
        if data[-8:] != FirebeatExe.PPP_IMAGE_FOOTER:
            raise Exception("Invalid footer!")

        # Now, grab the size of the embedded image.
        size = struct.unpack(">I", data[8:12])[0]

        # Compare to the size of the data, including the header preamble
        # and the footer.
        if (size + 32 + 8) != len(data):
            raise Exception("Invalid image size!")

        # Grab the compressed bit out, decompress it and return
        return FirebeatExe.__simple_exe_to_raw(data[32:-8])

    @staticmethod
    def exe_to_raw(data: bytes, *, is_ppp: bool = False) -> bytes:
        if is_ppp:
            return FirebeatExe.__ppp_exe_to_raw(data)
        else:
            return FirebeatExe.__simple_exe_to_raw(data)

    @staticmethod
    def __simple_raw_to_exe(data: bytes) -> bytes:
        header = struct.pack("<I", len(data))
        lz = LZSSFakeCompressor(data)
        return header + lz.compressed

    @staticmethod
    def __ppp_raw_to_exe(data: bytes) -> bytes:
        # First, compress the raw data
        compressed = FirebeatExe.__simple_raw_to_exe(data)

        # Now, construct a valid image header
        header = (
            FirebeatExe.PPP_IMAGE_HEADER +
            struct.pack(">II", len(compressed), FirebeatExe.PPP_LOAD_OFFSET) +
            b"\x00" * 16
        )

        # Now, return the image itself
        return header + compressed + FirebeatExe.PPP_IMAGE_FOOTER

    @staticmethod
    def raw_to_exe(data: bytes, *, is_ppp: bool = False) -> bytes:
        if is_ppp:
            return FirebeatExe.__ppp_raw_to_exe(data)
        else:
            return FirebeatExe.__simple_raw_to_exe(data)
