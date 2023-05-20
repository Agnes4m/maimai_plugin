from nonebot import on_command, on_notice
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, Event, Bot, MessageSegment
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot_plugin_txt2img import Txt2Img
from nonebot import get_driver
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from .libraries.image import *

from bs4 import BeautifulSoup
from typing import Dict,List
import aiohttp
from io import BytesIO
import json

try:
    maimai_font: str = get_driver().config.maimai_font
except:
    maimai_font: str = 'simsun.ttc'
try:
    b_cookie: str = get_driver().config.b_cookie
except:
    b_cookie: str = ''

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
分数线 <难度+歌曲id> <分数线> 详情请输入“分数线 帮助”查看'''
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



search = on_command('search',aliases={'b站搜索','mai搜索'})
@search.handle()
async def _(state: T_State,matcher:Matcher ,arg:Message = CommandArg()):
    msg = arg.extract_plain_text()
    data_list:List[Dict[str,Dict[str,str]]] = await get_target(msg)
    state['msg'] = data_list
    result_img = await data_to_img(data_list)
    img = BytesIO()
    result_img.save(img,format="png")
    img_bytes = img.getvalue()
    await matcher.send(MessageSegment.image(img_bytes))

@search.got("tap",prompt="请输入需要的序号")
async def _(state: T_State,matcher:Matcher ):
    tag:Message = state['tap']
    tag = tag.extract_plain_text()
    if tag.isdigit() and int(tag) in range(1, 10):
        msg:List[Dict[str,Dict[str,str]]] = state['msg']
        Url = msg[int(tag)-1]['url']['视频链接:']
        print(msg[int(tag)-1])
        await matcher.finish(Url)
    
async def fetch_page(url, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            return await response.text()    
    
async def get_target(keyword:str):
    headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
    'cookie': b_cookie
    }

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


async def make_dict_img(data: Dict[str, str], cell_width: int, cell_height: int, font_size: int) -> Image:
    img = Image.new('RGBA', (cell_width, cell_height), color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(maimai_font, font_size)

    i = 0
    for k, v in data.items():
        lentext = f"{k}{v}"
        while len(lentext) > 0:
            draw.text((10, i * (font_size + 5)), lentext[:25], font=font, fill=(0, 0, 0, 255))
            lentext = lentext[25:]
            i += 1

    return img


async def data_to_img(msg_list: List[Dict[str, Dict[str, str]]], cell_width=1080//3, cell_height=1920//3, font_size=20) -> Image:
    cols = 3
    rows = 3

    # 创建一张1080*1920的空白图
    result_img = Image.new('RGBA', (cell_width * cols, cell_height * rows), color=(255, 255, 255, 255))

    # 将每个dict对象转换成包含两个dict对象的列表
    data_list = []
    for msg in msg_list:
        data = msg['data']
        url = msg['url']
        data_list.append((url, data))

    for i, (url, data) in enumerate(data_list):
        # 将图片缩放并插入到格子中
        image_content = await fetch_page(url['封面:'], headers={
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
        })
        image = Image.open(BytesIO(image_content))
        img_width, img_height = image.size
        ratio = min(cell_width/img_width, cell_height/img_height)
        new_width = int(img_width*ratio)
        new_height = int(img_height*ratio)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)
        img_x = ((i % cols) * cell_width) + ((cell_width - new_width) // 2)
        img_y = ((i // cols) * cell_height) + ((cell_height - new_height-200) // 2)
        result_img.paste(image, (img_x, img_y))
 

        # 添加文字信息到下方
        dict_img = await make_dict_img(data, cell_width, cell_height, font_size)
        dict_x = ((i % cols) * cell_width) + ((cell_width - dict_img.size[0]) // 2)
        dict_y = ((i // cols) * cell_height) + new_height + ((cell_height - new_height - font_size - dict_img.size[1]) // 2) + new_height*1
        result_img.paste(dict_img, (dict_x, dict_y))

    return result_img

