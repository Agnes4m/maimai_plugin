import asyncio
import json
import random
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, List, Set, Union

import aiohttp
import httpx
from bs4 import BeautifulSoup
from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment

# from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher

# from nonebot.message import event_preprocessor
from nonebot.params import CommandArg, RawCommand
from nonebot_plugin_txt2img import Txt2Img
from pydantic import BaseModel, Extra

from .api import update_pl
from .libraries.image import *


class Config(BaseModel):
    """基本配置"""

    bot_nickname: str = "宁宁"
    maimai_font: str = "simsun.ttc"
    master_id: Union[List[str], Set[str]] = get_driver().config.superusers
    b_cookie: str = "b_nut=1649576401; buvid3=1E315685-39D7-CED8-F3F1-243C09E1F2E402464infoc; i-wanna-go-back=-1; buvid_fp_plain=undefined; CURRENT_BLACKGAP=0; LIVE_BUVID=AUTO8116495836832058; blackside_state=0; PVID=1; buvid4=1978384A-7128-E8DD-7067-595341C2F6BB02464-022041015-GcxPOTfDq8w%2FtuBv55%2BLdQ%3D%3D; rpdid=|(YuRll)|~l0J'uYY)mJJRl|; CURRENT_FNVAL=4048; header_theme_version=CLOSE; fingerprint=6b47357ae6c97f2cdf90243e8c57b973; CURRENT_PID=eada9510-d0f2-11ed-b243-8b1406a7fccc; DedeUserID=60824233; DedeUserID__ckMd5=7cfd5a1f149fedcc; b_ut=5; _uuid=1E6E8C21-4FC6-8F106-EE71-4210107CEF105DF35899infoc; FEED_LIVE_VERSION=V8; nostalgia_conf=-1; bp_video_offset_60824233=792868838749241300; CURRENT_QUALITY=64; home_feed_column=5; SESSDATA=b8c82b67%2C1704203767%2Ce49ff%2A71-fAq4c-tiCsv2xLJKAbdwkmTP4VbOeQWX9DmlCZBeKungWYZDVcsCMNDVohyiVIpNtJ4kQAAIQA; bili_jct=ac45f014bd11b174389d07077744f044; buvid_fp=a275cb625909c14200ae434eefcc8d94; browser_resolution=1492-771"

    class Config:
        extra = Extra.ignore


config = Config.parse_obj(get_driver().config)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0",
    "cookie": config.b_cookie,
}


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
async def _():
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
    title = "可用命令如下："
    txt2img = Txt2Img()
    txt2img.set_font_size(font_size=32)
    pic = txt2img.draw(title, help_str)
    try:
        await help.send(MessageSegment.image(pic))
    except Exception:
        await help.send(help_str)


search = on_command("搜手元", aliases={"搜理论", "搜谱面确认"})


@search.handle()
async def _(matcher: Matcher, command: str = RawCommand(), arg: Message = CommandArg()):
    keyword = command.replace("搜", "")
    msgs = arg.extract_plain_text()
    if not msgs:
        await matcher.finish("请把要搜索的内容放在后面哦")
    data_list: List[Dict[str, Dict[str, str]]] = await get_target(keyword + msgs)
    msg = data_list

    choice_dict = random.randint(1, len(data_list))
    #     result_img = await data_to_img(data_list)
    #     img = BytesIO()
    #     result_img.save(img,format="png")
    #     img_bytes = img.getvalue()
    #     await matcher.send(MessageSegment.image(img_bytes))

    # @search.got("tap",prompt="请输入需要的序号")
    # async def _(state: T_State,matcher:Matcher ):
    # tags:Message = state['tap']
    # tag = tags.extract_plain_text()
    # if tag.isdigit() and int(tag) in range(1, 10):
    print(msg[choice_dict])
    # msg:List[Dict[str,Dict[str,str]]] = state['msg']
    Url = msg[int(choice_dict) - 1]["url"]["视频链接:"]
    title = msg[int(choice_dict) - 1]["data"]["视频标题:"]
    pic = msg[int(choice_dict) - 1]["url"]["封面:"]
    await matcher.send(title + MessageSegment.image(pic) + Url)
    # try:
    Url = Url.replace("\n", "").replace("\r", "")
    # await b_to_url(Url, matcher=matcher, video_title=title)
    # await matcher.finish(MessageSegment.video(Url))
    # except Exception as E:
    #         logger.warning(E)
    # await matcher.finish(Url)


async def fetch_page(url):
    # print(headers)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            return await response.text()


async def get_target(keyword: str):
    mainurl = "https://search.bilibili.com/all?keyword=" + keyword
    content = await fetch_page(mainurl)
    mainsoup = BeautifulSoup(content, "html.parser")
    viedoNum = 1
    msg_list: List[Dict[str, Dict[str, str]]] = []
    for item in mainsoup.find_all("div", class_="bili-video-card"):
        item: BeautifulSoup
        msg: Dict[str, Dict[str, str]] = {"data": {}, "url": {}}
        # try:
        msg["data"]["序号:"] = "第" + viedoNum.__str__() + "个视频:"
        val = item.find("div", class_="bili-video-card__info--right")
        if val:
            msg["data"]["视频标题:"] = val.find("h3", class_="bili-video-card__info--tit")[  # type: ignore
                "title"
            ]  # type: ignore
            msg["url"]["视频链接:"] = "https:" + val.find("a")["href"] + "\n"  # type: ignore
            try:
                msg["data"]["up主:"] = item.find(
                    "span",
                    class_="bili-video-card__info--author",
                ).text.strip()  # type: ignore
                msg["data"]["视频观看量:"] = item.select(
                    "span.bili-video-card__stats--item span",
                )[0].text.strip()
            except (AttributeError, IndexError):
                continue

            msg["data"]["弹幕量:"] = item.select("span.bili-video-card__stats--item span")[
                1
            ].text.strip()
            msg["data"]["上传时间:"] = item.find(
                "span",
                class_="bili-video-card__info--date",
            ).text.strip()  # type: ignore
            msg["data"]["视频时长:"] = item.find(
                "span",
                class_="bili-video-card__stats__duration",
            ).text.strip()  # type: ignore
            msg["url"]["封面:"] = "https:" + item.find("img").get("src")  # type: ignore
            # except:
            #     continue
            msg_list.append(msg)
            if viedoNum == 9:
                break
            viedoNum += 1
    return msg_list


def getDownloadUrl(url: str):
    """
        爬取下载链接
    :param url:
    :return:
    """
    with httpx.Client(follow_redirects=True) as client:
        resp = client.get(url, headers=headers)
        print(resp.text)
        info = re.search(
            r"<script>window\.__playinfo__=({.*})<\/script><script>",
            resp.text,
        )[  # type: ignore
            1
        ]  # type: ignore
        res: dict = json.loads(info)
        videoUrl: str = (
            res["data"]["dash"]["video"][0]["baseUrl"]
            or res["data"]["dash"]["video"][0]["backupUrl"][0]
        )
        audioUrl: str = (
            res["data"]["dash"]["audio"][0]["baseUrl"]
            or res["data"]["dash"]["audio"][0]["backupUrl"][0]
        )
        if videoUrl and audioUrl:
            return videoUrl, audioUrl
        return None


async def downloadBFile(url, fullFileName, progressCallback):
    """
        下载视频文件和音频文件
    :param url:
    :param fullFileName:
    :param progressCallback:
    :return:
    """
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url, headers=headers) as resp:
            currentLen = 0
            totalLen = int(resp.headers["content-length"])
            print(totalLen)
            with Path(fullFileName).open("wb") as f:
                async for chunk in resp.aiter_bytes():
                    currentLen += len(chunk)
                    f.write(chunk)
                    progressCallback(currentLen / totalLen)


def mergeFileToMp4(
    vFullFileName: str,
    aFullFileName: str,
    outputFileName: str,
    shouldDelete=True,
):
    """
        合并视频文件和音频文件
    :param vFullFileName:
    :param aFullFileName:
    :param outputFileName:
    :param shouldDelete:
    :return:
    """
    # 调用ffmpeg
    subprocess.call(
        f'ffmpeg -y -i "{vFullFileName}" -i "{aFullFileName}" -c copy "{outputFileName}"',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # 删除临时文件
    if shouldDelete:
        Path(vFullFileName).unlink()
        Path(aFullFileName).unlink()


def delete_boring_characters(sentence):
    """
        去除标题的特殊字符
    :param sentence:
    :return:
    """
    return re.sub(
        "[0-9’!\"∀〃#$%&'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~～\s]+",
        "",
        sentence,  # type: ignore
    )


async def b_to_url(url: str, matcher: Matcher, video_title: str):
    # 获取视频信息
    base_video_info = "http://api.bilibili.com/x/web-interface/view"
    video_id = re.search(r"video\/[^\?\/ ]+", url)[0].split("/")[1]  # type: ignore
    logger.info(video_id)
    video_titles = httpx.get(  # noqa: ASYNC100
        f"{base_video_info}?bvid={video_id}"
        if video_id.startswith("BV")
        else f"{base_video_info}?aid={video_id}",
    )
    if video_titles.status_code != 200:
        await matcher.finish(f"{url}\nck已失效，请尝试重新获取")
    video_title = video_titles.json()["data"]["title"]
    video_title = delete_boring_characters(video_title)
    video_title = re.sub(r'[\\/:*?"<>|]', "", video_title)
    # 获取下载链接
    video_url, audio_url = getDownloadUrl(url)  # type: ignore
    # 下载视频和音频
    path = video_title
    await asyncio.gather(
        downloadBFile(video_url, f"{video_title}-video.m4s", logger.info),
        downloadBFile(audio_url, f"{video_title}-audio.m4s", logger.info),
    )
    mergeFileToMp4(
        f"{video_title}-video.m4s",
        f"{video_title}-audio.m4s",
        f"{path}-res.mp4",
    )
    # logger.info(os.getcwd())
    # 发送出去
    # logger.info(path)
    await matcher.send(MessageSegment.video(f"{path}-res.mp4"))
    # logger.info(f'{path}-res.mp4')
    # 清理文件
    Path(f"{video_title}-res.mp4").unlink()
    Path(f"{video_title}-res.mp4.jpg").unlink()


async def check_mai(force: bool = False):  # noqa: FBT001
    """检查mai资源"""
    await update_pl()  # 获取json文件
    if not Path(STATIC).joinpath("mai/pic").exists() or force:
        logger.info("初次使用，正在尝试自动下载资源\n资源包大小预计90M")
        try:
            response = httpx.get(  # noqa: ASYNC100
                "https://www.diving-fish.com/maibot/static.zip",
            )  # noqa: ASYNC100
            static_data = response.content

            with Path("static.zip").open("wb") as f:
                f.write(static_data)
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
