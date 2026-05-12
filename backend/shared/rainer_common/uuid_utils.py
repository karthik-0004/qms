"""UUID utility — UUID v7 generator (RFC 9562, time-ordered)."""

import os
import time
import uuid as _uuid_mod

__all__ = ["uuid7"]


def uuid7() -> str:
    """Return a new UUID v7 string (48-bit ms timestamp + random bits, sortable)."""
    ts_ms = int(time.time() * 1000) & 0xFFFF_FFFF_FFFF  # 48-bit millisecond timestamp
    rand = int.from_bytes(os.urandom(10), "big")           # 80 random bits
    rand_a = (rand >> 68) & 0xFFF                           # 12 bits → rand_a field
    rand_b = rand & 0x3FFF_FFFF_FFFF_FFFF                  # 62 bits → rand_b field
    # upper 64: [48 ts][4 ver=7][12 rand_a]
    upper = (ts_ms << 16) | (0x7 << 12) | rand_a
    # lower 64: [2 variant=10][62 rand_b]
    lower = 0x8000_0000_0000_0000 | rand_b
    return str(_uuid_mod.UUID(int=(upper << 64) | lower))
