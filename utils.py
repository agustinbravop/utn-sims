def bits_a_kb(bits: int) -> int:
    """Pasa de bits a kilobytes."""
    return bits // 8 // 1024


def kb_a_bits(kilobytes: int) -> int:
    """Pasa de kilobytes a bits."""
    return kilobytes * 8 * 1024
