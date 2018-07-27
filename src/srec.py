import logging
from typing import Generator, Iterable, Optional

from srecord import SRecord, Purpose

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


def to_binary(srecords: Iterable[SRecord], page_size: Optional[int] = None) -> Generator[bytearray, None, None]:
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
