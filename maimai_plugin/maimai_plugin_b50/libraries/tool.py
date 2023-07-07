import time
import httpx
import zipfile

# import io
# from tqdm import tqdm
from pathlib import Path
from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger


STATIC = get_res_path("maimai_plugin").joinpath("static")
STATIC.parent.mkdir(parents=True, exist_ok=True)
STATIC = str(STATIC)
download_url = "https://www.diving-fish.com/maibot/static.zip"


async def check_mai():
    """检查mai资源"""
    if not Path(STATIC).joinpath("mai/pic").exists():
        logger.debug("初次使用，正在尝试自动下载资源\n资源包大小预计90M")
        try:
            response = httpx.get(download_url)
            static_data = response.content

            with open("static.zip", "wb") as f:
                f.write(static_data)

            with zipfile.ZipFile("static.zip", "r") as zip_file:
                zip_file.extractall(STATIC)

            Path("static.zip").unlink()  # 删除下载的压缩文件
        except Exception as e:
            logger.warning(f"自动下载出错\n{e}\n请自行尝试手动下载")


def hash(qq: int):
    days = (
        int(time.strftime("%d", time.localtime(time.time())))
        + 31 * int(time.strftime("%m", time.localtime(time.time())))
        + 77
    )
    return (days * qq) >> 8
