from nonebot import on_command, on_notice
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, Event, Bot, MessageSegment
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot_plugin_txt2img import Txt2Img
from nonebot import get_driver
from nonebot.params import CommandArg
from .libraries.image import *

from bs4 import BeautifulSoup
from typing import Dict,List
import httpx
from io import BytesIO
import json

try:
    maimai_font: str = get_driver().config.maimai_font
except:
    maimai_font: str = 'simsun.ttf'
try:
    b_cookie: str = get_driver().config.b_cookie
except:
    b_cookie: str = 'simsun.ttf'

@event_preprocessor
async def preprocessor(bot, event, state):
    if hasattr(event, 'message_type') and event.message_type == "private" and event.sub_type != "friend":
        raise IgnoredException("not reply group temp message")

        
help = on_command('help',aliases={'舞萌帮助','mai帮助'})


@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
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
async def _(arg:Message = CommandArg()):
    msg = arg.extract_plain_text()
    data_list = await get_target(msg)
    result_img = await data_to_img(data_list)
    img = BytesIO()
    result_img.save(img,format="png")
    img_bytes = img.getvalue()
    await search.finish(MessageSegment.image(img_bytes))


async def get_target(keyword:str):
    headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
    'cookie': b_cookie
    }

    mainUrl='https://search.bilibili.com/all?keyword='+keyword
    mainSoup = BeautifulSoup(httpx.get(url = mainUrl, headers= headers).text, "html.parser")
    viedoNum = 0
    msg_list = []
    for item in mainSoup.find_all('div',class_="bili-video-card"):
        item:BeautifulSoup
        viedoNum += 1
        msg = {'data':{},'url':{}}
        try:
            msg['data']['序号:'] = '第'+ viedoNum.__str__() + '个视频:'
            val=item.find('div',class_="bili-video-card__info--right")
            msg['data']['视频标题:'] =  val.find('h3',class_="bili-video-card__info--tit")['title']
            msg['url']['视频链接:'] = 'https:'+ val.find('a')['href'] + '\n'
            msg['data']['up主:'] = item.find('span',class_="bili-video-card__info--author").text.strip()
            msg['data']['视频观看量:'] = item.select('span.bili-video-card__stats--item span')[0].text.strip()
            msg['data']['弹幕量:'] =  item.select('span.bili-video-card__stats--item span')[1].text.strip()
            msg['data']['上传时间:'] = item.find('span',class_='bili-video-card__info--date').text.strip()
            msg['data']['视频时长:'] = item.find('span',class_='bili-video-card__stats__duration').text.strip()
            msg['url']['封面:'] = 'https:'+ item.find('img').get('src')
        except:
            continue
        print(json.dumps(msg,indent=4,ensure_ascii=False) )
        msg_list.append(msg)
        if viedoNum == 9:
            break
    return msg_list


async def data_to_img(msg_list:List[Dict[str,dict]]):
    
    # 定义常量
    PADDING = 30
    FONT_SIZE = 40
    LINE_SPACING = 20
    TEXT_COLOR = (255, 255, 255, 255)
    response = httpx.get(url = msg_list[0]['url']['封面:'])
    img = Image.open(BytesIO(response.content))

    # 计算宽高和每个格子的宽高
    width, height = img.size
    cell_width = (width - PADDING * 2) // 3
    cell_height = (height - PADDING * 2) // 3

    # 新建一张空白图片
    result_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # 获取字体
    print(maimai_font)
    font = ImageFont.truetype(maimai_font,30)
    for data in msg_list:
        # 在每个格子中插入图片和文字
        for i, d in enumerate(data['data']):
            # 计算格子的左上角坐标
            x = (i % 3) * cell_width + PADDING
            y = (i // 3) * cell_height + PADDING

            # 将图片缩放并插入到格子中
            response =  httpx.get(data['url']['封面:'])
            image = Image.open(BytesIO(response.content)).resize((cell_width, cell_height), Image.ANTIALIAS)
            result_img.paste(image, (x, y))

            # 绘制文字
            draw = ImageDraw.Draw(result_img)
            text = '\n'.join(list(d.values()))
            w, h = draw.multiline_textsize(text, font=font)
            draw.text((x + cell_width / 2 - w / 2, y + cell_height), text, fill=TEXT_COLOR, font=font, align='center', spacing=LINE_SPACING)

    return result_img