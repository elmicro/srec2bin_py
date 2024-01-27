#-----------------------------------------------------------------------------
#
#   srecord.py - Handling Module for Motorola S-Records
#   by Oliver Thamm - ELMICRO Computer
#   https://github.com/elmicro/srec2bin_py
#
#   This software is Copyright (C)2017 by ELMICRO - https://elmicro.com
#   and may be freely used, modified and distributed under the terms of
#   the MIT License - see accompanying LICENSE.md for details
#
#-----------------------------------------------------------------------------

class SRecord:

    _type2asiz = {"S0":2, "S1":2, "S2":3, "S3":4, "S5":2, "S6":3, "S7":4, "S8":3, "S9":2}

    def __init__(self):
        self.type = ""
        self.addr = 0
        self.data = bytearray()
        self.error = ""

    def process(self, srecline):
        """ determine type and starting address of a single S-Record line,
            extract data bytes, verify syntax and checksum, ignore any
            blank lines, return an empty string "" on success,
            otherwise a string containing the error description
        """
        self.type = ""
        self.addr = 0
        self.data = bytearray()

        # determine length of input
        self.line = srecline.rstrip()
        self.line_len = len(self.line)
        # gracefully ignore an empty line
        if self.line_len == 0:
            self.error = ""
            return self.error

        # check size limits and test for even number of chars
        if self.line_len < 10 or self.line_len > 514 or self.line_len % 2:
            self.error = "s-record has wrong size"
            return self.error

        self.type = self.line[:2]
        self.addr_siz = self._type2asiz.get(self.type, 0)
        if not self.addr_siz:
            self.error = "s-record type unknown"
            return self.error

        # construe char pairs as hex values
        try:
            self.values = bytearray([int(self.line[i:i+2], 16) for i in range(2,self.line_len, 2)])
        except ValueError:
            self.error = "s-record contains invalid character(s)"
            return self.error

        # check byte count field vs. number of char pairs
        if self.values[0] != len(self.values)-1:
            self.error = "s-record byte count mismatch"
            return self.error

        # determine starting address
        self.addr = self.values[1] * 0x100 + self.values[2]
        if self.addr_siz > 2:
            self.addr = self.addr * 0x100 + self.values[3]
        if self.addr_siz > 3:
            self.addr = self.addr * 0x100 + self.values[4]

        # verify check sum
        if sum(self.values, 1) % 0x100:
            self.error = "s-record checksum error"
            return self.error

        # deliver the data bytes
        self.data = self.values[self.addr_siz+1:-1]
        self.error = ""
        return self.error

#-----------------------------------------------------------------------------
