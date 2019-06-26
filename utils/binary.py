from typing import List, Tuple


class Binary:

    @staticmethod
    def diff(bin1: bytes, bin2: bytes) -> List[str]:
        if len(bin1) != len(bin2):
            raise Exception("Cannot diff different-sized binary blobs!")

        # First, get the list of differences
        differences: List[Tuple[int, bytes, bytes]] = []
        for i in range(len(bin1)):
            byte1 = bin1[i:(i+1)]
            byte2 = bin2[i:(i+1)]

            if byte1 != byte2:
                differences.append((i, byte1, byte2))

        # Don't bother with any combination crap if we have nothing to do
        if not differences:
            return []

        # Now, combine them for easier printing
        cur_block: Tuple[int, bytes, bytes] = differences[0]
        ret: List[str] = []

        def _hex(val: int) -> str:
            out = hex(val)[2:]
            out = out.upper()
            if len(out) == 1:
                out = "0" + out
            return out

        def _hexrun(val: bytes) -> str:
            return " ".join(_hex(v) for v in val)

        def _output(val: Tuple[int, bytes, bytes]) -> None:
            start = val[0] - len(val[1]) + 1

            ret.append(
                f"{_hex(start)}: {_hexrun(val[1])} -> {_hexrun(val[2])}"
            )

        def _combine(val: Tuple[int, bytes, bytes]) -> None:
            nonlocal cur_block

            if cur_block[0] + 1 == val[0]:
                # This is a continuation of a run
                cur_block = (
                    val[0],
                    cur_block[1] + val[1],
                    cur_block[2] + val[2],
                )
            else:
                # This is a new run
                _output(cur_block)
                cur_block = val

        # Combine and output runs of differences
        for diff in differences[1:]:
            _combine(diff)

        # Make sure we output the last difference
        _output(cur_block)

        # Return our summation
        return ret
