from enum import Enum
from typing import AnyStr


# -----------------------------------------------------------------------------
#
#   srecord.py - Handling Module for Motorola S-Records
#   by Oliver Thamm - Elektronikladen Microcomputer
#   https://github.com/elmicro/srec2bin_py
#
#   This software is Copyright (C)2017 by ELMICRO - https://elmicro.com
#   and may be freely used, modified and distributed under the terms of
#   the MIT License - see accompanying LICENSE.md for details
#
# -----------------------------------------------------------------------------


class ParseException(Exception):
    pass


class Purpose(Enum):
    Header = 0
    Data = 1
    Count = 2
    StartAddress = 3


class Type(Enum):
    S0 = 0
    S1 = 1
    S2 = 2
    S3 = 3
    S5 = 5
    S6 = 6
    S7 = 7
    S8 = 8
    S9 = 9


TypePurpose = {
    Type.S0: Purpose.Header,
    Type.S1: Purpose.Data,
    Type.S2: Purpose.Data,
    Type.S3: Purpose.Data,
    Type.S5: Purpose.Count,
    Type.S6: Purpose.Count,
    Type.S7: Purpose.StartAddress,
    Type.S8: Purpose.StartAddress,
    Type.S9: Purpose.StartAddress,
}

TypeAddressSize = {
    Type.S0: 2,
    Type.S1: 2,
    Type.S2: 3,
    Type.S3: 4,
    Type.S5: 2,
    Type.S6: 3,
    Type.S7: 4,
    Type.S8: 3,
    Type.S9: 2
}


class SRecord:
    """
    An SRecord is an ASCII string of the following structure:
    S | Type | Count | Address | Data | Checksum
    S : The character 'S'(0x53)
    Type : a numeric digit defining the type of the record
    Count : two hex digits indicating the number of bytes in the rest of the record
    Address : 4, 6 or 8 hex digits depending on record type in big endian
    Data : a sequence of 2n hex digits for n bytes of data
    Checksum : two hex digits, the least significant byte of ones' compliment of the sum of values of the count,
    address and data fields
    """

    def __init__(self, source: AnyStr):
        self.type: Type = None
        self.byte_count: int = 0
        self.address: int = 0
        self.data: bytes = None
        self.checksum: int = None
        self.__process(source)

    def __repr__(self):
        address_formatter = "{{:0{}X}}".format(self.address_length * 2)
        formatter = "{} {:02x} " + address_formatter + " {} {:02X}"
        return formatter.format(self.type.name, self.byte_count, self.address, self.data.hex().upper(), self.checksum)

    def __process(self, source: AnyStr):
        """ determine type and starting address of a single S-Record line,
            extract data bytes, verify syntax and checksum, ignore any
            blank lines, return an empty string "" on success,
            otherwise a string containing the error description
        """
        # determine length of input
        source = source.rstrip()
        # gracefully ignore an empty line
        if len(source) == 0:
            return

        assert 2 < len(source), ParseException("Truncated S-record: " + source)

        try:
            self.type = Type[source[:2]]
        except KeyError:
            ParseException("Incorrect S-record type specification: " + source[:2])

        try:
            self.byte_count = int(source[2:4], 16)
            assert (self.byte_count << 1) == (len(source[4:])), \
                ParseException("Incorrect byte count(actual: {}; specified: {})".format(
                    len(source[4:]) >> 1,
                    self.byte_count))

            self.address = int(source[4:4 + (self.address_length << 1)], 16)
            self.data = bytes.fromhex(source[4 + (self.address_length << 1):2 + (self.byte_count << 1)])
            self.checksum = int(source[-2:], 16)
        except Exception as e:
            raise ParseException("Invalid characters in S-record") from e

        calculated_checksum = (sum(int(source[i:i + 2], 16) for i in range(2, len(source) - 2, 2)) & 0xFF) ^ 0xFF
        assert self.checksum == calculated_checksum, \
            ParseException("Incorrect checksum: {} != {}".format(self.checksum, calculated_checksum))

    @property
    def address_length(self):
        return TypeAddressSize[self.type]

    @property
    def purpose(self):
        return TypePurpose[self.type]

# -----------------------------------------------------------------------------
