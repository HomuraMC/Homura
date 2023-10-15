"""
The 8-bit float formats used here are from a proposal supported by Graphcore, AMD and Qualcomm.
See https://arxiv.org/abs/2206.02915

"""

import struct
import zlib

# When uncompressed this gives the conversion from every possible float16 value to a float8_143 value.
lut_float16_to_float8_143_compressed = b"x\x01\xed\xdde\xb6\x96\x05\x00E\xe1\x8f\xee\x06\xe9FZA\xa4\xbb\xbb;\xa4SB\xba\xeb\xd2\xdd\x8dt\x97\x92J(\xa14\xa2\x84" \
    b"\x92\x8a\xa4\x82\xd2\x1d\x12\x0e\xe2\xfe\xd8k\xf1\xeeg\x06gO\xe0\x84B\xb2\x80\x05,`\x01\x0bX\xc0\x02\x16\xb0\x80\x05,`\x01\x0bX\xc0\x02\x16\xb0\x80\x05\xde" \
    b"\xd7\x02\x11d\x01\x0b\x04\xb6@D\x05\xba@$\x05\xba@\xe4\x80\x8b\x12pQ\x03.Z\xc0E\x87\xc5\x80\xc5\x84\xc5\x82\xc5\x86\xc5\x81\xc5\x85\xc5\x83\xc5\x87%\x80%\x84" \
    b"%\x82%\x86%\x81}\x00K\nK\x06K\x0eK\x01K\tK\x05K\rK\x03K\x0bK\x07K\x0f\xcb\x00\xcb\x08\xcb\x04\xfb\x10\x96\x19\x96\x05\x96\x15\x96\r\x96\x1d\x96\x03\x96\x13" \
    b"\xf6\x11\xeccX.Xn\xd8'\xb0<\xb0Oaya\xf9`\xf9a\x05`\x05a\x85`\x85aE`Ea\xc5`\xc5a%`%a\xa5`\xa5ae`ea\xe5`\xe5a\x15`\x15a\x95`\x95aU`Ua\xd5`\xd5a5`5a\xb5`\xb5au`" \
    b"ua\xf5`\xf5a\r`\ra\x8d`\x8daM`\x9f\xc1\x9a\xc2\x9a\xc1\x9a\xc3Z\xc0Z\xc2Z\xc1Z\xc3\xda\xc0\xda\xc2\xda\xc1\xda\xc3:\xc0>\x87u\x84u\x82u\x86u\x81}\x01\xeb\n" \
    b"\xeb\x06\xeb\x0e\xeb\x01\xeb\t\xeb\x05\xeb\r\xeb\x03\xeb\x0b\xeb\x07\xeb\x0f\x1b\x00\x1b\x08\x1b\x04\x1b\x0c\x1b\x02\x1b*\x0bX\xc0\x02\x16\xb0\x80\x05,`\x01" \
    b"\x0bX\xc0\x02\x16\xb0\x80\x05,`\x01\x0bX\xc0\x02\x16\xb0\x80\x05,`\x01\x0bX\xc0\x02\x16\xb0\x80\x05,\x10\xde\x02a\xb2\x80\x05\x82Z\xe0}\xfd5s\x97\x05,`\x01" \
    b"\x0bX\xc0\x02\x16\xb0\x80\x05,`\x01\x0bX\xc0\x02\x16\xb0\x80\x05,\x10\n\r\x93\x05,\x10\xd8\x02\xc3\x15\xe8\x02#\x14\xe8\x02#\x03nT\xc0\x8d\x0e\xb81\x017\x166" \
    b"\x0e6\x1e6\x016\x116\t6\x196\x056\x156\r6\x1d6\x036\x136\x0b6\x1b6\x076\x176\x0f6\x1f\xf6%l\x01l!l\x11l1l\tl)l\x19l9l\x05l%l\x15l5l\rl-l\x1dl=l\x03\xec+\xd8" \
    b"\xd7\xb0\x8d\xb0M\xb0\xcd\xb0-\xb0\xad\xb0m\xb0o`\xdf\xc2\xb6\xc3v\xc0v\xc2v\xc1\xbe\x83}\x0f\xdb\r\xdb\x03\xdb\x0b\xdb\x07\xfb\x01\xf6#l?\xec\x00\xec \xec" \
    b"\x10\xec0\xec\x08\xec(\xec\x18\xec'\xd8q\xd8\xcf\xb0_`'`'a\xa7`\xa7a\xbf\xc2~\x83\x9d\x81\x9d\x85\x9d\x83\x9d\x87]\x80]\x84\xfd\x0e\xfb\x03v\t\xf6'\xec2\xec" \
    b"\n\xec*\xec\x1a\xec:\xec\x06\xec/\xd8\xdf\xb0\x9b\xb0[\xb0\x7f`\xff\xc2n\xc3\xee\xc0\xee\xc2\xee\xc1\xee\xc3\x1e\xc0\x1e\xc2\x1e\xc1\x1e\xc3\x9e\xc0\x9e\xc2" \
    b"\x9e\xc1\x9e\xc3^\xc0^\xc2^\xc1\xfe\x83\xbd\x86\xbd\x81\xbd\x85\xbd\x93\x05,`\x01\x0bX\xc0\x02\x16\xb0\x80\x05,`\x01\x0bX\xc0\x02\x16\xb0\x80\x05,`\x01\x0bX" \
    b"\xc0\x02\x16\xb0\x80\x05,`\x01\x0bX\xc0\x02\x16\x08o\x81\xa0\x1e\x9f\xbb\xdb\x02\x16\x08\xfb\x1f\x0b\xd9\xb3x"

# When uncompressed this gives the conversion from every possible float16 value to a float8_152 value.
lut_float16_to_float8_152_compressed = b'x\x01\xed\xdde\xa2\x16T\x00E\xd1\x07\n\x82R\x92J\nJHK7"\xa1H#\xd2HIwwI\xa7R\xd2H\xab(\xdd%(\xadt\x89A\xa7\xd2\xdd1\x8c' \
    b'\xfbc}k\x06gO\xe0DE\x85\x15-\xb0\xe8\x81\xbd\x12\xd8\xab\x81\xc5\x08,f`\xaf\x05\x16\x0b\x17\x1b\xf7:\xee\r\\\x1c\\\\\\<\\|\\\x02\xdc\x9b\xb8\x84\xb8D\xb8\xc4' \
    b'\xb8$\xb8\xa4\xb8d\xb8\xb7po\xe3\x92\xe3R\xe0R\xe2R\xe1R\xe3\xd2\xe0\xde\xc1\xa5\xc5\xa5\xc3\xbd\x8b{\x0f\x97\x1e\x97\x01\x97\x11\x97\t\xf7>.3.\x0b.+.\x1b.;.' \
    b'\x07.\'\xee\x03\\.\\n\\\x1e\\^\\>\\~\\\x01\\A\\!\\a\\\x11\\Q\\1\\q\xdc\x87\xb8\x12\xb8\x8fp%q\xa5p\xa5qep\x1f\xe3>\xc1\x95\xc5}\x8a+\x87+\x8f\xab\x80\xab\x88' \
    b'\xab\x84\xab\x8c\xab\x82\xab\x8a\xfb\x0cW\r\xf79\xae:\xae\x06\xae&\xae\x16\xae6\xae\x0e\xae.\xae\x1e\xee\x0b\\}\\\x03\\C\\#\\c\xdc\x97\xb8&\xb8\xa6\xb8f\xb8' \
    b'\xe6\xb8\x16\xb8\x96\xb8V\xb8\xd6\xb86\xb8\xb6\xb8v\xb8\xf6\xb8\x0e\xb8\x8e\xb8N\xb8\xce\xb8.\xb8\xae\xb8n\xb8\xee\xb8\x1e\xb8\x9e\xb8^\xb8\xde\xb8>\xb8\xbe' \
    b'\xb8~\xba\xfe\x11\x91\x02\x91\x02j\x81\xa8\xc0\x06\x04\xf6U`\x03\x03\x1b\x14\xd8\xe0\xc0\x86\x0464\xb0a\xb8\xe1\xb8\x11\xb8\x91\xb8Q\xb8\xd1\xb81\xb8\xafq' \
    b'\xdf\xe0\xc6\xe2\xc6\xe1\xc6\xe3&\xe0&\xe2\xbe\xc5M\xc2M\xc6M\xc1M\xc5M\xc3M\xc7\xcd\xc0\xcd\xc4}\x87\x9b\x85\x9b\x8d\x9b\x83\x9b\x8b\x9b\x87\x9b\x8f[\x80' \
    b'\xfb\x1e\xf7\x03\xeeG\xdcB\xdcO\xb8\x9fq\x8bp\x8bqKpKq\xcbp\xcbq+p+q\xabp\xabqkpkq\xebp\xebq\x1bp\x1bq\x9bp\xbf\xe06\xe3\xb6\xe0~\xc5\xfd\x86\xdb\x8a\xdb' \
    b'\x86\xdb\x8e\xdb\x81\xdb\x89\xdb\x85\xdb\x8d\xfb\x1d\xf7\x07n\x0fn/n\x1fn?\xee\x00\xee \xee\x10\xee0\xee\x08\xee(\xee\x18\xeeO\xdcq\xdc_\xb8\xbfq\xff\xe0\xfe' \
    b'\xc5\x9d\xc0\x9d\xc4\x9d\xc2\x9d\xc6\x9d\xc1\x9d\xc5\x9d\xc3\x9d\xc7]\xc0]\xc4]\xc2]\xc6\xfd\x87\xfb\x1fw\x05w\x15w\rw\x1dw\x03w\x13w\x0bw\x1bw\x07w\x17w\x0f' \
    b'w\x1f\xf7\x00\xf7\x10\xf7\x08\xf7\x18\xf7\x04\xf7\x14\xf7\x0c\xf7\x1c\xf7B\xa7\x1e\x9fGvG\nD\n\xf4\x7f\tz_,\x0e'

# When uncompressed this maps each single byte integer to the Python float value that it represents when interpreted as a float8_143 value.
lut_int8_to_float8_143_compressed = b'x\x01\x15\xcc[\xb5\x90!\x10\x80Q"\x18\x81\x08<\xabGQ\x0b\x10\x81\x084\x90\x08D \x02\xcf^\xd1S\xe0\x8f@\x04"\xb8e\xad=/3\x1f!\xfc\x7f\xfd\xad\xf1.\x84Lg\xb29' \
    b'\x84\xf7!\xbc!\x92\xc8\x14*\x8d\xce`\xb2\xd8<\x1c.\xe1EO$\x91)T\x1a\x9d\xc1d\xb1y8\\\xc2\x07=\x91D\xa6Pit\x06\x93\xc5\xe6\xe1p\t\x1f\xf5D\x12\x99B\xa5\xd1\x19' \
    b'L\x16\x9b\x87\xc3%d=\x91D\xa6Pit\x06\x93\xc5\xe6\xe1p\t\x9f\xf4D\x12\x99B\xa5\xd1\x19L\x16\x9b\x87\xc3%|\xd6\x13Id\n\x95Fg0Yl\x1e\x0e\x97\xf0EO$\x91)T\x1a\xfb' \
    b'\xab?\xbe\xb9\xfbnGg\xb29\x84\x1fz"\x89L\xa1\xd2\xe8\x0c&\x8b\xcd\xc3\xe1\x12~\xea\x89$2\x85J\xa33\x98,6\x0f\x87K\xf8\xa5\'\x92\xc8\x14*\x8d\xce`\xb2\xd8<\x1c' \
    b'.\xe1\xb7\x9eH"S\xa84:\x83\xc9b\xf3p\xb8\x84\xad\'\x92\xc8\x14*\x8d\xce`\xb2\xd8<\x1c.\xe1\x8f\x9eH"S\xa84:\x83\xc9b\xf3p\xb8\x84\xbfz"\x89L\xa1\xd2\xe8\x0c&\x8b' \
    b'\xcd\xc3\xe1\x12^\xf5D\x12\x99B\xa5\xbd\xfe\x03\xc2b\xf2\xc8'

# When uncompressed this maps each single byte integer to the Python float value that it represents when interpreted as a float8_152 value.
lut_int8_to_float8_152_compressed = b'x\x01\x1d\xca\xd9\x11\x10\x06\x08EQJ\xb1\x0b\x8d[\xd0\xb8\xb4A\'R\n]\xc45\xc1\xb8\xb5A)\x9e\t3\xe7\x87\xfb"\xfe\xbf\x87\x11\xcd\x12\x8f"\x1e\x90\x14\xcd\xb0\x1c' \
    b'\xf1\x87NR4\xc3r\xc4c\x9d\xa4h\x86\xe5\x88\':I\xd1\x0c\xcb\x11Ou\x92\xa2\x19\x96#\x9e\xe9$E3,G<\xd7I\x8afX\x8e\xf8S\')\x9aa9"u\x92\xa2\x19\x96#^\xe8$E3,G\xbc\xd4' \
    b'I\x8afX\x8e\xf8K\')\x9aa9\xe2\x95NR4\xc3r\xc4k\x9d\xa4h\x86\xe5\x887:I\xd1\x0c\xcb\x11ou\x92b\xdf\xf9\xfdm\xc7\x12\xefu\x92\xa2\x19\x96#>\xe8$E3,G|\xd4I\x8afX' \
    b'\x8e\xf8\xa4\x93\x14\xcd\xb0\x1c\xf1Y\')\x9aa9\xe2\x8bNR4\xc3r\xc4?:I\xd1\x0c\xcb\x11\xff\xea$E3,G\xacNR4\xc3r\xc4W\x9d\xa4h\x86\xe5\x88\xfft\x92\xa2\x19\x96#' \
    b'\xbe\xe9$E3,G|\xd7I\x8afX\x8e\xf8\xa1\x93\x14\xcd\xb0\x1c\xf1S\')\x9aa9\xe2\x97NR\xbf~\x03\x96j\xecR'


class FP8Format:
    """Defining an 8-bit floating point format"""

    def __init__(self, exp_bits: int, bias: int):
        # We use look up tables to go from an IEEE float16 to the best float8 representation.
        # For startup efficiency they've been precalculated and zipped up
        if exp_bits == 4 and bias == 8:
            self.lut_float16_to_float8 = zlib.decompress(lut_float16_to_float8_143_compressed)
            self.lut_int8_to_float = struct.unpack('<256f', zlib.decompress(lut_int8_to_float8_143_compressed))
        elif exp_bits == 5 and bias == 16:
            self.lut_float16_to_float8 = zlib.decompress(lut_float16_to_float8_152_compressed)
            self.lut_int8_to_float = struct.unpack('<256f', zlib.decompress(lut_int8_to_float8_152_compressed))
        else:  # pragma: no cover
            raise RuntimeError("Unsupported float8 format trying to be created. Only float8_143 and float8_152 available for now.")
            # # This is how the LUTs above were calculated. For reference only - shouldn't be needed any more
            # self.lut_int8_to_float = self.createLUT_for_int8_to_float()
            # self.lut_float16_to_float8 = self.createLUT_for_float16_to_float8()
            # # Then we used a line like this to create the constants:
            # lut_float16_to_float8_143_compressed = zlib.compress(self.lut_float16_to_float8, 1)
            # # See also the test_fp8.py unit tests which check the equivalence.

    def float_to_int8(self, f: float) -> int:
        """Given a Python float convert to the best float8 (expressed as an integer in 0-255 range)."""
        # First convert the float to a float16, then a 16 bit uint
        try:
            b = struct.pack('>e', f)
        except (OverflowError, struct.error):
            # Return the largest representable positive or negative value
            return 0b01111111 if f > 0 else 0b11111111
        f16_int = int.from_bytes(b, byteorder='big')
        # Then use this as an index to our large LUT
        return self.lut_float16_to_float8[f16_int]


# We create the 1.5.2 and 1.4.3 formats. The proposed 1.3.4 format isn't supported here.
fp143_fmt = FP8Format(exp_bits=4, bias=8)
fp152_fmt = FP8Format(exp_bits=5, bias=16)