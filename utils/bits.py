def as_bits(x: int, n: int) -> str:
    return f'{x:0{n}b}'


def as_bits_reversed(x: int, n: int) -> str:
    return as_bits(x, n)[::-1]
