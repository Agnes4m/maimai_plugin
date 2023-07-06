from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message,  MessageSegment
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot_plugin_txt2img import Txt2Img
from nonebot.log import logger
from nonebot import get_driver
from nonebot.params import CommandArg,RawCommand
from nonebot.matcher import Matcher
from .libraries.image import *

from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict,List
import aiohttp
import os
import json
import random
import subprocess
import httpx
import re
import asyncio

try:
    maimai_font: str = get_driver().config.maimai_font
except:
    maimai_font: str = 'simsun.ttc'
try:
    b_cookie: str = get_driver().config.b_cookie
except:
    b_cookie: str = ''
headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
    'cookie': b_cookie
    }


@event_preprocessor
async def preprocessor(bot, event, state):
    if hasattr(event, 'message_type') and event.message_type == "private" and event.sub_type != "friend":
        raise IgnoredException("not reply group temp message")

        
help = on_command('help',aliases={'舞萌帮助','mai帮助'})


@help.handle()
async def _():
    help_str = '''可用命令如下：
今日舞萌 查看今天的舞萌运势
XXXmaimaiXXX什么 随机一首歌
随个[dx/标准][绿黄红紫白]<难度> 随机一首指定条件的乐曲
查歌<乐曲标题的一部分> 查询符合条件的乐曲
[绿黄红紫白]id<歌曲编号> 查询乐曲信息或谱面信息
<歌曲别名>是什么歌 查询乐曲别名对应的乐曲
定数查歌 <定数>  查询定数对应的乐曲
定数查歌 <定数下限> <定数上限>
分数线 <难度+歌曲id> <分数线> 详情请输入“分数线 帮助”查看
搜<手元><理论><谱面确认>'''
    # await help.send(Message([
    #     MessageSegment("image", {
    #         "file": f"base64://{str(image_to_base64(text_to_image(help_str)), encoding='utf-8')}"
    #     })
    # ]))
    title = '可用命令如下：'
    txt2img = Txt2Img()
    txt2img.set_font_size(font_size = 32)
    pic = txt2img.draw(title, help_str)
    try:
        await help.send(MessageSegment.image(pic))
    except:
        await help.send(help_str)



search = on_command('搜手元',aliases={'搜理论','搜谱面确认'})
@search.handle()
async def _(matcher:Matcher ,command: str = RawCommand(),arg:Message = CommandArg()):
    keyword = command.replace('搜','')
    msgs = arg.extract_plain_text()
    if not msgs:
        await matcher.finish('请把要搜索的内容放在后面哦')
    data_list:List[Dict[str,Dict[str,str]]] = await get_target(keyword+msgs)
    msg= data_list
    
    choice_dict = random.randint(1,len(data_list))
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
    
        # msg:List[Dict[str,Dict[str,str]]] = state['msg']
    Url = msg[int(choice_dict)-1]['url']['视频链接:']
    title = msg[int(choice_dict)-1]['data']['视频标题:']
    await matcher.send(title)
    try:
        await b_to_url(Url,matcher=matcher)
        # await matcher.finish(MessageSegment.video(Url))
    except Exception as E:
        logger.warning(E)
        await matcher.finish(Url)
    
async def fetch_page(url, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            return await response.text()    
    
async def get_target(keyword:str):


    mainUrl='https://search.bilibili.com/all?keyword='+keyword
    content = await fetch_page(mainUrl, headers)
    mainSoup = BeautifulSoup(content, "html.parser")
    viedoNum = 1
    msg_list = []
    for item in mainSoup.find_all('div',class_="bili-video-card"):
        item:BeautifulSoup
        msg = {'data':{},'url':{}}
        # try:
        msg['data']['序号:'] = '第'+ viedoNum.__str__() + '个视频:'
        val=item.find('div',class_="bili-video-card__info--right")
        msg['data']['视频标题:'] =  val.find('h3',class_="bili-video-card__info--tit")['title']
        msg['url']['视频链接:'] = 'https:'+ val.find('a')['href'] + '\n'
        try:
            msg['data']['up主:'] = item.find('span',class_="bili-video-card__info--author").text.strip()
            msg['data']['视频观看量:'] = item.select('span.bili-video-card__stats--item span')[0].text.strip()
        except (AttributeError,IndexError):
            continue
        
        msg['data']['弹幕量:'] =  item.select('span.bili-video-card__stats--item span')[1].text.strip()
        msg['data']['上传时间:'] = item.find('span',class_='bili-video-card__info--date').text.strip()
        msg['data']['视频时长:'] = item.find('span',class_='bili-video-card__stats__duration').text.strip()
        msg['url']['封面:'] = 'https:'+ item.find('img').get('src')
        # except:
        #     continue
        print(json.dumps(msg,indent=4,ensure_ascii=False) )
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
        info = re.search(r"<script>window\.__playinfo__=({.*})<\/script><script>", resp.text)[1]
        res = json.loads(info)
        videoUrl = res["data"]["dash"]["video"][0]["baseUrl"] or res["data"]["dash"]["video"][0]["backupUrl"][0]
        audioUrl = res["data"]["dash"]["audio"][0]["baseUrl"] or res["data"]["dash"]["audio"][0]["backupUrl"][0]
        if videoUrl != "" and audioUrl != "":
            return videoUrl, audioUrl

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
            totalLen = int(resp.headers['content-length'])
            print(totalLen)
            with open(fullFileName, "wb") as f:
                async for chunk in resp.aiter_bytes():
                    currentLen += len(chunk)
                    f.write(chunk)
                    progressCallback(currentLen / totalLen)


def mergeFileToMp4(vFullFileName: str, aFullFileName: str, outputFileName: str, shouldDelete=True):
    """
        合并视频文件和音频文件
    :param vFullFileName:
    :param aFullFileName:
    :param outputFileName:
    :param shouldDelete:
    :return:
    """
    # 调用ffmpeg
    subprocess.call(f'ffmpeg -y -i "{vFullFileName}" -i "{aFullFileName}" -c copy "{outputFileName}"', shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    )
    # 删除临时文件
    if shouldDelete:
        os.unlink(vFullFileName)
        os.unlink(aFullFileName)
        
        
def delete_boring_characters(sentence):
    """
        去除标题的特殊字符
    :param sentence:
    :return:
    """
    return re.sub('[0-9’!"∀〃#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~～\s]+', "", sentence)

async def b_to_url(url:str,matcher:Matcher):
     # 获取视频信息
    base_video_info = "http://api.bilibili.com/x/web-interface/view"
    video_id = re.search(r"video\/[^\?\/ ]+", url)[0].split('/')[1]
    # logger.info(video_id)
    video_title = httpx.get(
        f"{base_video_info}?bvid={video_id}" if video_id.startswith(
            "BV") else f"{base_video_info}?aid={video_id}").json()[
        'data']['title']
    video_title = delete_boring_characters(video_title)
    # video_title = re.sub(r'[\\/:*?"<>|]', "", video_title)
    # 获取下载链接
    video_url, audio_url = getDownloadUrl(url)
    # 下载视频和音频
    path = video_title
    await asyncio.gather(
        downloadBFile(video_url, f"{video_title}-video.m4s", logger.info),
        downloadBFile(audio_url, f"{video_title}-audio.m4s", logger.info))
    mergeFileToMp4(f"{video_title}-video.m4s", f"{video_title}-audio.m4s", f"{path}-res.mp4")
    # logger.info(os.getcwd())
    # 发送出去
    # logger.info(path)
    await matcher.send(MessageSegment.video(f'{path}-res.mp4'))
    # logger.info(f'{path}-res.mp4')
    # 清理文件
    os.unlink(f"{video_title}-res.mp4")
    os.unlink(f"{video_title}-res.mp4.jpg")
