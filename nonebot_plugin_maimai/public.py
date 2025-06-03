import zipfile
from pathlib import Path
from typing import List, Set, Union

import aiofiles
import httpx
from nonebot import get_driver, on_command

# from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher

# from nonebot.message import event_preprocessor
from pydantic import BaseModel

from .api import update_pl
from .libraries.image import *


class Config(BaseModel):
    """基本配置"""

    bot_nickname: str = "宁宁"
    maimai_font: str = "simsun.ttc"
    master_id: Union[List[str], Set[str]] = get_driver().config.superusers

    class Config:
        extra = "ignore"


config = Config.parse_obj(get_driver().config)


# @event_preprocessor
# async def preprocessor(bot: Bot, event:Event, state):
#     if (
#         hasattr(event, "message_type")
#         and event.message_type == "private"
#         and event.sub_type != "friend"
#     ):
#         raise IgnoredException("not reply group temp message")


help_msg = on_command("help", aliases={"舞萌帮助", "mai帮助"})


@help_msg.handle()
async def _(matcher: Matcher):
    help_str = """可用命令如下：
今日舞萌 查看今天的舞萌运势
XXXmaimaiXXX什么 随机一首歌
随个[dx/标准][绿黄红紫白]<难度> 随机一首指定条件的乐曲
查歌<乐曲标题的一部分> 查询符合条件的乐曲
[绿黄红紫白]id<歌曲编号> 查询乐曲信息或谱面信息
<歌曲别名>是什么歌 查询乐曲别名对应的乐曲
定数查歌 <定数>  查询定数对应的乐曲
定数查歌 <定数下限> <定数上限>
分数线 <难度+歌曲id> <分数线> 详情请输入“分数线 帮助”查看
搜<手元><理论><谱面确认>"""
    # await help.send(Message([
    #     MessageSegment("image", {
    #         "file": f"base64://{str(image_to_base64(text_to_image(help_str)), encoding='utf-8')}"
    #     })
    # ]))
    await matcher.send(help_str)


async def check_mai(force: bool = False):  # noqa: FBT001
    """检查mai资源"""
    await update_pl()  # 获取json文件
    if not Path(STATIC).joinpath("mai/pic").exists() or force:
        logger.info("初次使用，正在尝试自动下载资源\n资源包大小预计90M")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.diving-fish.com/maibot/static.zip",
                )
                static_data = response.content

            async with aiofiles.open("static.zip", "wb") as f:
                await f.write(static_data)
            logger.success("已成功下载，正在尝试解压mai资源")
            with zipfile.ZipFile("static.zip", "r") as zip_file:
                zip_file.extractall(Path("data/maimai"))
            logger.success("mai资源已完整，尝试删除缓存")
            Path("static.zip").unlink()  # 删除下载的压缩文件
            msg = "mai资源下载成功，请使用【舞萌帮助】获取指令"

        except Exception as e:
            logger.warning(f"自动下载出错\n{e}\n请自行尝试手动下载")
            msg = f"自动下载出错\n{e}\n请自行尝试手动下载"
        return msg
    logger.info("已经成功下载，无需下载")
    return "已经成功下载，无需下载"
