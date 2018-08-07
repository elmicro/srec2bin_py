import logging
from typing import Generator, Iterable, Tuple, Optional

from .srecord import SRecord, Purpose

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

MAX_PAGE_SIZE = 0x100000


def load(filename: str):
    if isinstance(filename, str):
        with open(filename, 'r') as f:
            srecords = (SRecord(line) for line in f.readlines())
    else:
        srecords = (SRecord(line) for line in filename)

    return srecords


def to_image(srecords: Iterable[SRecord], fill_byte: bytes = b'\xff', offset: int = 0) -> Tuple[bytearray, int]:
    log.debug("Converting SRecords to binary, fill: 0x{}, offset: 0x{:x}".format(fill_byte.hex(), offset))

    target_memory = bytearray(fill_byte * 0x100000)
    target_memmap = bytearray(0x100000 * b'\xff')
    byte_cnt = 0
    high_address = 0
    for srecord in srecords:
        if srecord.purpose == Purpose.Data:
            addr = srecord.address - offset
            log.debug("Processing SRecord: {} @ 0x{:08x}".format(srecord, addr))
            for b in srecord.data:
                if target_memmap[addr] == 0:
                    log.debug("Non critical error: duplicate access to address: 0x{:04X}; {}".format(addr, srecord))
                else:
                    byte_cnt += 1
                target_memmap[addr] = 0
                target_memory[addr] = b
                addr += 1
            if addr > high_address:
                high_address = addr
        else:
            log.debug("Skipping non-data line")

    return target_memory[:high_address], byte_cnt


def to_pages(srecords: Iterable[SRecord], page_size: Optional[int] = None) -> Generator[
    Tuple[int, bytearray], None, None]:
    page_size = page_size or MAX_PAGE_SIZE
    log.debug("Converting SRecords to binary, page_size: 0x{:x}".format(page_size))

    page = bytearray()

    page_address = -1
    for srecord in srecords:
        if srecord.purpose == Purpose.Data:
            log.debug("Processing SRecord: {}".format(srecord))
            if page_address < 0:
                page_address = srecord.address

            elif srecord.address < page_address or srecord.address >= (page_address + page_size):
                log.debug("Switching from page at 0x{:08X} to 0x{:08X}".format(page_address, srecord.address))
                yield page_address, page
                page = bytearray()
                page_address = srecord.address

            if len(page) + len(srecord.data) >= page_size:
                remaining = page_size - len(page)
                page[len(page):] = srecord.data[:remaining]
                yield page_address, page
                page = bytearray(srecord.data[remaining:])
                page_address = srecord.address + remaining
            else:
                page[len(page):] = srecord.data[:]

    if page:
        yield page_address, page
