from typing import Tuple, Generator

AnyDimensionalTuple = Tuple[int, ...]
ndt = AnyDimensionalTuple
RGBTuple = Tuple[int, int, int]


def any_range(c1: ndt, c2: ndt) -> Generator[ndt, None, None]:
    assert len(c1) == len(c2)
    x, c1 = c1[0], c1[1:]
    y, c2 = c2[0], c2[1:]

    lower, upper = [(x, y), (y, x)][x > y]

    for n in range(lower, upper + 1):
        if not (c1 and c2):
            yield (n,)
        else:
            for down in any_range(c1, c2):
                yield (n, *down)