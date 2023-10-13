import asyncio
import json
import re
from typing import Any, Dict, List, Optional

import aiohttp
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.models import Message as Messages
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV

from .public import *

try:
    from .libraries.image import (
        image_to_base64,
        text_to_image,
        url_to_base64,
        url_to_bytes,
    )
except Exception as E:
    logger.warning(E)
from .libraries.maimai_best_40 import generate
from .libraries.maimai_best_50 import generate50
from .libraries.maimaidx_music import Music, get_cover_len5_id, total_list
from .libraries.tool import _hash, check_mai

sv = SV(
    name="基础指令",  # 定义一组服务`开关`,
    pm=6,  # 权限 0为master，1为superuser，2为群的群主, 3为管理员，6为普通，具体可见文档
    priority=50,  # 整组服务的优先级
    enabled=True,  # 是否启用
    black_list=[],  # 黑名单
    area="GROUP",  # 作用范围，可选'GROUP', 'DIRECT', 'ALL'
)


def song_txt(music: Music) -> List[Messages]:
    return [
        Messages(
            "text",
            f"{music.id}. {music.title}\n",
        ),
        MessageSegment.image(
            url_to_bytes(
                f"https://www.diving-fish.com/covers/{get_cover_len5_id(music.id)}.png"  # type: ignore
            ),
        ),
        Messages("text", f"\n{'/'.join(music.level)}"),  # type: ignore
    ]


def inner_level_q(ds1: float, ds2: Optional[float] = None):
    result_set = []
    diff_label = ["Bas", "Adv", "Exp", "Mst", "ReM"]
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in sorted(music_data, key=lambda i: int(i["id"])):
        for i in music.diff:
            result_set.append(
                (
                    music["id"],
                    music["title"],
                    music["ds"][i],
                    diff_label[i],
                    music["level"][i],
                )
            )
    return result_set


@sv.on_command(("inner_level", "定数查歌"))
async def inner_level(bot: Bot, event: Event):
    argv = event.text.split(" ")
    if len(argv) > 2 or len(argv) == 0:
        await bot.send("命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>")
        return
    if len(argv) == 1:
        result_set = inner_level_q(float(argv[0]))
    else:
        result_set = inner_level_q(float(argv[0]), float(argv[1]))
    if len(result_set) > 50:
        await bot.send(f"结果过多（{len(result_set)} 条），请缩小搜索范围。")
        return
    s = ""
    for elem in result_set:
        s += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    await bot.send(s.strip())


@sv.on_regex(r"^随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?")
async def spec_rand(bot: Bot, event: Event):
    message = event.raw_text
    regex = r"随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, str(message).lower())
    if res:
        try:
            if res.groups()[0] == "dx":
                tp = ["DX"]
            elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
                tp = ["SD"]
            else:
                tp = ["SD", "DX"]
            level = res.groups()[2]
            if res.groups()[1] == "":
                music_data = total_list.filter(level=level, type=tp)
            else:
                music_data = total_list.filter(
                    level=level, diff=["绿黄红紫白".index(res.groups()[1])], type=tp
                )
            if len(music_data) == 0:
                rand_result = "没有这样的乐曲哦。"
            else:
                rand_result = song_txt(music_data.random())
            await bot.send(rand_result)
        except Exception as e:
            print(e)
            await bot.send("随机命令错误，请检查语法")


@sv.on_regex(r".*maimai.*什么")
async def mr(bot: Bot):
    await bot.send(song_txt(total_list.random()))


@sv.on_regex(r"^查歌.+")
async def search_music(bot: Bot, event: Event):
    regex = "查歌(.+)"
    message = event.raw_text
    name = re.match(regex, str(message))
    if name:
        name = name.groups()[0].strip()
    if not name:
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        await bot.send("没有找到这样的乐曲。")
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key=lambda i: int(i["id"])):
            search_result += f"{music['id']}. {music['title']}\n"
        await bot.send(search_result.strip())
    else:
        await bot.send(f"结果过多（{len(res)} 条），请缩小查询范围。")


@sv.on_regex(r"^([绿黄红紫白]?)id([0-9]+)")
async def query_chart(bot: Bot, event: Event):
    regex = "([绿黄红紫白]?)id([0-9]+)"
    message = event.raw_text
    groups = re.match(regex, str(message))
    if not groups:
        return
    else:
        groups = groups.groups()
    level_labels = ["绿", "黄", "红", "紫", "白"]
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = [
                "Basic",
                "Advanced",
                "Expert",
                "Master",
                "Re: MASTER",
            ]
            name = groups[1]
            music = total_list.by_id(name)
            if music:
                chart = music["charts"][level_index]
                ds = music["ds"][level_index]
                level = music["level"][level_index]
                file = f"https://www.diving-fish.com/covers/{get_cover_len5_id(music['id'])}.png"
                if len(chart["notes"]) == 4:
                    msg = f"""{level_name[level_index]} {level}({ds})
    TAP: {chart['notes'][0]}
    HOLD: {chart['notes'][1]}
    SLIDE: {chart['notes'][2]}
    BREAK: {chart['notes'][3]}
    谱师: {chart['charter']}"""
                else:
                    msg = f"""{level_name[level_index]} {level}({ds})
    TAP: {chart['notes'][0]}
    HOLD: {chart['notes'][1]}
    SLIDE: {chart['notes'][2]}
    TOUCH: {chart['notes'][3]}
    BREAK: {chart['notes'][4]}
    谱师: {chart['charter']}"""
                await bot.send(
                    Messages(
                        "text",
                        f"{music['id']}. {music['title']}\n",
                    )
                    + Messages("image", url_to_base64(file))
                    + Messages("text", msg)
                )

        except Exception:
            await bot.send("未找到该谱面")
    else:
        name = groups[1]
        music = total_list.by_id(name)
        if music:
            try:
                file = f"https://www.diving-fish.com/covers/{get_cover_len5_id(music['id'])}.png"
                await query_chart.send(
                    f"{music['id']}. {music['title']}\n"
                    + Messages("image", f"{file}")
                    + f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"
                )
            except Exception:
                await bot.send("未找到该乐曲")
        else:
            await bot.send("未找到该乐曲")


wm_list = [
    "拼机",
    "推分",
    "越级",
    "下埋",
    "夜勤",
    "练底力",
    "练手法",
    "打旧框",
    "干饭",
    "抓绝赞",
    "收歌",
]


@sv.on_fullmatch(("今日舞萌", "今日mai"))
async def jrwm(bot: Bot, event: Event):
    qq = int(event.user_id)
    h = _hash(qq)
    rp = h % 100
    wm_value = []
    for i in range(11):
        wm_value.append(h & 3)
        h >>= 2
    s = f"今日人品值：{rp}\n"
    for i in range(11):
        if wm_value[i] == 3:
            s += f"宜 {wm_list[i]}\n"
        elif wm_value[i] == 0:
            s += f"忌 {wm_list[i]}\n"
    s += "mai-bot提醒您：打机时不要大力拍打或滑动哦\n今日推荐歌曲："
    music = total_list[h % len(total_list)]

    await bot.send([Messages("text", s)] + (song_txt(music)))


@sv.on_command("分数线")
async def query_score(bot: Bot, event: Event):
    r = "([绿黄红紫白])(id)?([0-9]+)"
    message = event.raw_text
    argv = str(message).strip().split(" ")
    if len(argv) == 1 and argv[0] == "帮助":
        s = """此功能为查找某首歌分数线设计。
命令格式：分数线 <难度+歌曲id> <分数线>
例如：分数线 紫799 100
命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。
以下为 TAP GREAT 的对应表：
GREAT/GOOD/MISS
TAP\t1/2.5/5
HOLD\t2/5/10
SLIDE\t3/7.5/15
TOUCH\t1/2.5/5
BREAK\t5/12.5/25(外加200落)"""
        await bot.send(
            Messages(
                "image",
                f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}",
            )
        )
    elif len(argv) == 2:
        try:
            grp = re.match(r, argv[0])
            if grp:
                grp = grp.groups()
                level_labels = ["绿", "黄", "红", "紫", "白"]
                level_labels2 = [
                    "Basic",
                    "Advanced",
                    "Expert",
                    "Master",
                    "Re:MASTER",
                ]
                level_index = level_labels.index(grp[0])
                chart_id = grp[2]
                line = float(argv[1])
                music = total_list.by_id(chart_id)
                if not music:
                    raise Exception("没有这首歌")
                chart: Dict[str, Any] = music["charts"][level_index]  # type: ignore
                tap = int(chart["notes"][0])
                slide = int(chart["notes"][2])
                hold = int(chart["notes"][1])
                touch = int(chart["notes"][3]) if len(chart["notes"]) == 5 else 0
                brk = int(chart["notes"][-1])
                total_score = (
                    500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
                )
                break_bonus = 0.01 / brk
                break_50_reduce = total_score * break_bonus / 4
                reduce = 101 - line
                if reduce <= 0 or reduce >= 101:
                    raise ValueError
                await bot.send(
                    f"""{music['title']} {level_labels2[level_index]}
    分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
    BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)"""
                )
        except Exception:
            await bot.send("格式错误，输入“分数线 帮助”以查看帮助信息")


@sv.on_command("b40")
async def best_40_pic(bot: Bot, event: Event):
    payload = at_to_usrid(event, "b40")
    img, success = await generate(payload)
    if success == 400 or not img:
        await bot.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await bot.send("该用户禁止了其他人获取数据。")
    else:
        await bot.send(
            Messages(
                "image",
                f"base64://{str(image_to_base64(img), encoding='utf-8')}",
            )
        )


@sv.on_command("b50")
async def best_50_pic(bot: Bot, event: Event):
    payload = at_to_usrid(event)
    img, success = await generate50(payload)
    if success == 400 or not img:
        await bot.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await bot.send("该用户禁止了其他人获取数据。")
    else:
        await bot.send(
            Messages(
                "image",
                f"base64://{str(image_to_base64(img), encoding='utf-8')}",
            )
        )


def at_to_usrid(event: Event, b: str = "b50"):
    """存在at优先，其次co_command,最后usr_id"""
    if event.at:
        return {"qq": event.at, b: True}
    elif event.text:
        return {"username": event.text, b: True}
    else:
        return {"qq": event.user_id, b: True}


@sv.on_command(("help", "舞萌帮助", "mai帮助"), block=True)
async def help(bot: Bot, event: Event):
    help_str: str = """可用命令如下：
今日舞萌 查看今天的舞萌运势
XXXmaimaiXXX什么 随机一首歌
随个[dx/标准][绿黄红紫白]<难度> 随机一首指定条件的乐曲
查歌<乐曲标题的一部分> 查询符合条件的乐曲
[绿黄红紫白]id<歌曲编号> 查询乐曲信息或谱面信息
<歌曲别名>是什么歌 查询乐曲别名对应的乐曲
定数查歌 <定数>  查询定数对应的乐曲
定数查歌 <定数下限> <定数上限>
分数线 <难度+歌曲id> <分数线> 详情请输入“分数线 帮助”查看
检查mai资源"""
    await bot.send(
        Messages(
            "image",
            f"base64://{str(image_to_base64(text_to_image(help_str)), encoding='utf-8')}",
        )
    )


@sv.on_fullmatch("检查mai资源")
async def check_mai_data(bot: Bot, event: Event):
    await bot.send("正在尝试下载，大概需要2-3分钟")
    logger.info("开始检查资源")
    await bot.send(await check_mai())


@sv.on_fullmatch("强制检查mai资源")
async def force_check_mai_data(bot: Bot, event: Event):
    await bot.send("正在尝试下载，大概需要2-3分钟")
    logger.info("开始检查资源")
    await bot.send(await check_mai(force=True))
