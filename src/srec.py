import logging
from typing import Tuple, Iterable

from srecord import SRecord, Purpose

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def load(filename: str):
    if isinstance(filename, str):
        with open(filename, 'r') as f:
            srecords = (SRecord(line) for line in f.readlines())
    else:
        srecords = (SRecord(line) for line in filename)

    return srecords


def to_binary(srecords: Iterable[SRecord], fill_byte: int = 0xff, offset: int = 0) -> Tuple[bytearray, int]:
    log.debug("Converting SRecords to binary, fill: 0x{:X}, offset: 0x{:x}".format(fill_byte, offset))

    target_memory = bytearray(0x100000 * fill_byte)
    target_memmap = bytearray(0x100000 * b'\xff')
    byte_cnt = 0
    high_address = 0
    for srecord in srecords:
        if srecord.type.value == Purpose.Data:
            addr = srecord.address - offset
            log.debug("Processing SRecord: {} @ 0x{}".format(srecord, addr))
            for b in srecord.data:
                if target_memmap[addr] != 0:
                    target_memmap[addr] = 0
                    target_memory[addr] = b
                    byte_cnt += 1
                else:
                    log.error("Non critical error: duplicate access to address: 0x{:04X}; {}".format(addr, srecord))
                addr += 1
            if addr > high_address:
                high_address = addr
        else:
            log.debug("Skipping non-data line")

    return target_memory[:high_address], byte_cnt
