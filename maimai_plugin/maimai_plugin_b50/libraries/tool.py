import time
import httpx
import zipfile
import aiohttp, asyncio
from typing import Union
from pathlib import Path
from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger


STATICs = get_res_path("maimai_plugin")
STATICs.parent.mkdir(parents=True, exist_ok=True)
STATIC = str(STATICs.joinpath("static"))
download_url = "https://www.diving-fish.com/maibot/static.zip"


async def check_mai(force: bool = False):
    """检查mai资源"""
    if not Path(STATIC).joinpath("mai/pic").exists() or force:
        logger.info("初次使用，正在尝试自动下载资源\n资源包大小预计90M")
        try:
            response = httpx.get(download_url)
            static_data = response.content

            with open("static.zip", "wb") as f:
                f.write(static_data)
            logger.success('已成功下载，正在尝试解压mai资源')
            with zipfile.ZipFile("static.zip", "r") as zip_file:
                zip_file.extractall(STATICs)
            logger.success('mai资源已完整，尝试删除缓存')
            # Path("static.zip").unlink()  # 删除下载的压缩文件
            return 'mai资源下载成功，请使用【舞萌帮助】获取指令'
        except Exception as e:
            logger.warning(f"自动下载出错\n{e}\n请自行尝试手动下载")
            return f"自动下载出错\n{e}\n请自行尝试手动下载"
    else:
        logger.info('已经成功下载，无需下载')
        return '已经成功下载，无需下载'


def hash(qq: int):
    days = (
        int(time.strftime("%d", time.localtime(time.time())))
        + 31 * int(time.strftime("%m", time.localtime(time.time())))
        + 77
    )
    return (days * qq) >> 8
