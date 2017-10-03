#!/usr/bin/env python

#-----------------------------------------------------------------------------
#
#   Motorola S-Record to Binary File Converter (Python 3)
#
#   by Oliver Thamm - Elektronikladen Microcomputer
#   https://github.com/elmicro/srec2bin_py
#
#   This software is Copyright (C)2017 by ELMICRO - https://elmicro.com
#   and may be freely used, modified and distributed under the terms of
#   the MIT License - see accompanying LICENSE.md for details
#
#-----------------------------------------------------------------------------

import os
import sys
import argparse
from srecord import *

#-- definitions --------------------------------------------------------------

SCRIPT_VERSION = '0.90'
DEFAULT_OUT_FILE_EXT = '.bin'
DEFAULT_OUT_FILE_NAME = 'out' + DEFAULT_OUT_FILE_EXT

#-----------------------------------------------------------------------------

def _mkofn(out_fn, in_fn):
    """ if output file name is not specified, derive from input file name """

    if out_fn is None:
        if in_fn == '<stdin>':
            return DEFAULT_OUT_FILE_NAME
        else:
            base, ext = os.path.splitext(in_fn)
            return base + DEFAULT_OUT_FILE_EXT
    return out_fn

#-----------------------------------------------------------------------------

def _auto_int(x):
    return int(x, 0)

#-----------------------------------------------------------------------------
# main program
#-----------------------------------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Motorola S-Record to Binary Converter V' + SCRIPT_VERSION)
    parser.add_argument(
        'srec_file',
        type=argparse.FileType('r'),
        nargs='?', default=sys.stdin,
        help='s-record file name (if not specified: read from stdin)')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='display additional runtime information')
    parser.add_argument(
        '-s', '--start_addr',
        type=_auto_int,
        default=0x00000,
        help='start address for output, default is 0')
    parser.add_argument(
        '-e', '--end_addr',
        type=_auto_int,
        default=0x10000,
        help='end address (last + 1) for output, default is 0x10000')
    parser.add_argument(
        '-f', '--fill_byte',
        type=_auto_int,
        default=0xff,
        help='fill byte for unoccupied space, default is 0xff')
    parser.add_argument(
        '-o', '--out_file',
        help='output file name, default is <srec_file>' + DEFAULT_OUT_FILE_EXT +
        ' or ' + DEFAULT_OUT_FILE_NAME + ' if input is STDIN')
    args = parser.parse_args()

    fill_byte = (args.fill_byte % 0x100).to_bytes(1, 'big')
    target_memory = bytearray(0x10000 * fill_byte)
    target_memmap = bytearray(0x10000 * b'\xff')

    if args.verbose:
        print("Start address: 0x{0:04x}".format(args.start_addr))
        print("End address: 0x{0:04x}".format(args.end_addr))
        print("Filling with: 0x{0:02x}".format(fill_byte[0]))

    srecs = []
    line_no = 1
    byte_cnt = 0
    for srec_line in args.srec_file:
        srec = SRecord()
        if not srec.process(srec_line):
            if srec.type == "S1":
                srecs.append(srec)
            else:
                if args.verbose:
                    print("Skipping", srec.type if srec.type!="" else "empty", "line")
        else:
            print("Error in", args.srec_file.name, "Line", str(line_no) + ":")
            # to display the offending line we better use bytes type here in case
            # the input is (mistakenly) binary stuff instead of a text file
            print(srec_line.rstrip().encode('ASCII', 'ignore'))
            print(srec.error)
            print('Program terminated.')
            sys.exit(1)
        line_no += 1

    if args.verbose:
        print("S-Record lines processed: {0:d}".format(line_no - 1))

    for srec in srecs:
        addr = srec.addr
        for b in srec.data:
            if target_memmap[addr] != 0:
                target_memmap[addr] = 0
                target_memory[addr] = b
                byte_cnt += 1
            else:
                print("Error: duplicate access to addr", "0x%04x" % addr)
            addr += 1

    if args.verbose:
        print("Total bytes processed: {0:d}".format(byte_cnt))

    out_file_name = _mkofn(args.out_file, args.srec_file.name)
    if args.verbose:
        print("Writing to output file", out_file_name)
    with open(out_file_name, 'wb') as outfile:
        outfile.write(target_memory[args.start_addr:args.end_addr])

#-----------------------------------------------------------------------------
