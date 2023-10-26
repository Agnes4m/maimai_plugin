import time
from pathlib import Path

try:
    STATIC = str(Path().joinpath("data/maimai"))
except FileNotFoundError:
    STATIC = str(Path(__file__).parent.parent)


def hash_(qq: int):
    days = (
        int(time.strftime("%d", time.localtime(time.time())))
        + 31 * int(time.strftime("%m", time.localtime(time.time())))
        + 77
    )
    return (days * qq) >> 8
