def get_bits(x, n):
    return [int(x) for x in '{:0{size}b}'.format(x, size=n)]


def as_bits(x: int, n: int) -> str:
    return f'{x:0{n}b}'


def as_bits_reversed(x: int, n: int) -> str:
    return as_bits(x, n)[::-1]
