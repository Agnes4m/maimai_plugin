import re
from typing import Any

from nonebot import get_driver, on_command, on_regex, require
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import CommandArg, EventMessage
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import UniMessage

from .api import bind_site, show_all  # noqa: F401
from .libraries.image import *
from .libraries.maimai_best_40 import generate
from .libraries.maimai_best_50 import generate50
from .libraries.maimaidx_music import *
from .libraries.tool import hash_
from .public import *

try:
    import ujson as json
except ImportError:
    import json

driver = get_driver()
try:
    nickname = next(iter(driver.config.nickname))
except Exception:
    nickname = "宁宁"


__version__ = "0.5.0"
__plugin_meta__ = PluginMetadata(
    name="舞萌maimai-bot",
    description="移植mai-bot,适用nonebot2的Maimai插件",
    usage="指令：舞萌帮助",
    type="application",
    homepage="https://github.com/Agnes4m/maimai_plugin",
    supported_adapters={"~onebot.v11"},
    extra={
        "version": __version__,
        "author": "Agnes4m <Z735803792@163.com>",
    },
)


def song_txt(music: Music):
    return UniMessage(
        MessageSegment("text", {"text": f"{music.id}. {music.title}\n"}),
        MessageSegment(
            "image",
            {
                "file": f"https://www.diving-fish.com/covers/{get_cover_len5_id(music.id)}.png",
            },
        ),
        MessageSegment("text", {"text": f"\n{'/'.join(music.level)}"}),  # type: ignore
    )


def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ["Bas", "Adv", "Exp", "Mst", "ReM"]
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in sorted(music_data, key=lambda i: int(i["id"])):  # type: ignore
        for i in music.diff:
            result_set.append(
                (
                    music["id"],
                    music["title"],
                    music["ds"][i],
                    diff_label[i],
                    music["level"][i],
                ),
            )
    return result_set


inner_level = on_command("inner_level ", aliases={"定数查歌 "})


@inner_level.handle()
async def _(matcher: Matcher, message: Message = CommandArg()):
    argv = str(message).strip().split(" ")
    if len(argv) > 2 or len(argv) == 0:
        await inner_level.finish(
            "命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>",
        )
    if len(argv) == 1:
        result_set = inner_level_q(float(argv[0]))
    else:
        result_set = inner_level_q(float(argv[0]), float(argv[1]))
    if len(result_set) > 50:
        await inner_level.finish(f"结果过多（{len(result_set)} 条），请缩小搜索范围。")
    s = ""
    for elem in result_set:
        s += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    await matcher.finish(s.strip())


spec_rand = on_regex(r"^随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?")


@spec_rand.handle()
async def _(matcher: Matcher, message: Message = EventMessage()):
    # level_labels = ["绿", "黄", "红", "紫", "白"]
    regex = "随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"  # type: ignore
    res = re.match(regex, str(message).lower())
    try:
        if res:
            if res.groups()[0] == "dx":
                tp = ["DX"]
            elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
                tp = ["SD"]
            else:
                tp = ["SD", "DX"]
            level = res.groups()[2]
            if res.groups()[1] == "":
                music_data = total_list.filter(level=level, type_=tp)
            else:
                music_data = total_list.filter(
                    level=level,
                    diff=["绿黄红紫白".index(res.groups()[1])],
                    type_=tp,
                )
            if len(music_data) == 0 or music_data is None:  # type: ignore
                await matcher.send("没有这样的乐曲哦。")
            else:
                await matcher.send(Message(song_txt(music_data.random())))
    except Exception as e:
        print(e)
        await matcher.finish("随机命令错误，请检查语法")


mr = on_regex(r".*maimai.*什么")


@mr.handle()
async def _():
    await song_txt(total_list.random()).finish()


search_music = on_regex(r"^查歌.+")


@search_music.handle()
async def _(matcher: Matcher, message: Message = EventMessage()):
    regex = "查歌(.+)"
    name = re.match(regex, str(message)).groups()[0].strip()  # type: ignore
    if name == "":
        return
    res = total_list.filter(title_search=name)
    if res is None:
        return
    if len(res) == 0:
        await search_music.send("没有找到这样的乐曲。")
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key=lambda i: int(i["id"])):
            search_result += f"{music['id']}. {music['title']}\n"
        await matcher.finish(
            Message([MessageSegment("text", {"text": search_result.strip()})]),
        )
    else:
        await matcher.send(f"结果过多（{len(res)} 条），请缩小查询范围。")


query_chart = on_regex(r"^([绿黄红紫白]?)id([0-9]+)")


@query_chart.handle()
async def _(matcher: Matcher, message: Message = EventMessage()):
    regex = "([绿黄红紫白]?)id([0-9]+)"
    groups = re.match(regex, str(message)).groups()  # type: ignore
    level_labels = ["绿", "黄", "红", "紫", "白"]
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ["Basic", "Advanced", "Expert", "Master", "Re: MASTER"]
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
                await matcher.send(
                    Message(
                        [
                            MessageSegment(
                                "text",
                                {"text": f"{music['id']}. {music['title']}\n"},
                            ),
                            MessageSegment("image", {"file": f"{file}"}),
                            MessageSegment("text", {"text": msg}),
                        ],
                    ),
                )
        except Exception:
            await matcher.send("未找到该谱面")
    else:
        name = groups[1]
        music = total_list.by_id(name)
        try:
            if not music:
                return
            file = f"https://www.diving-fish.com/covers/{get_cover_len5_id(music['id'])}.png"
            await query_chart.send(
                Message(
                    [
                        MessageSegment(
                            "text",
                            {"text": f"{music['id']}. {music['title']}\n"},
                        ),
                        MessageSegment("image", {"file": f"{file}"}),
                        MessageSegment(
                            "text",
                            {
                                "text": f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}",
                            },
                        ),
                    ],
                ),
            )
        except Exception:
            await matcher.send("未找到该乐曲")


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


jrwm = on_command("今日舞萌", aliases={"今日mai"})


@jrwm.handle()
async def _(event: Event, matcher: Matcher):
    qq = int(event.get_user_id())
    h = hash_(qq)
    rp = h % 100
    wm_value = []
    for i in range(11):  # noqa: B007
        wm_value.append(h & 3)
        h >>= 2
    s = f"今日人品值：{rp}\n"
    for i in range(11):
        if wm_value[i] == 3:
            s += f"宜 {wm_list[i]}\n"
        elif wm_value[i] == 0:
            s += f"忌 {wm_list[i]}\n"
    s += f"{nickname}提醒您：打机时不要大力拍打或滑动哦\n今日推荐歌曲："
    music = total_list[h % len(total_list)]
    await matcher.finish(
        Message([MessageSegment("text", {"text": s}), *song_txt(music)]),
    )


query_score = on_command("分数线")


@query_score.handle()
async def _(matcher: Matcher, message: Message = CommandArg()):
    r = "([绿黄红紫白])(id)?([0-9]+)"
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
        await matcher.send(
            Message(
                [
                    MessageSegment(
                        "image",
                        {
                            "file": f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}",
                        },
                    ),
                ],
            ),
        )
    elif len(argv) == 2:
        try:
            grp = re.match(r, argv[0]).groups()  # type: ignore
            level_labels = ["绿", "黄", "红", "紫", "白"]
            level_labels2 = ["Basic", "Advanced", "Expert", "Master", "Re:MASTER"]
            level_index = level_labels.index(grp[0])
            chart_id = grp[2]
            line = float(argv[1])
            music = total_list.by_id(chart_id)
            if not music:
                return
            chart: Dict[str, Any] = music["charts"][level_index]
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
                raise ValueError  # noqa: TRY301
            await matcher.send(
                f"""{music['title']} {level_labels2[level_index]}
分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)""",
            )
        except Exception:
            await matcher.send("格式错误，输入“分数线 帮助”以查看帮助信息")


best_40_pic = on_command("b40")


@best_40_pic.handle()
async def _(event: Event, matcher: Matcher, message: Message = CommandArg()):
    username = str(message).strip()
    at = await get_message_at(event.json())
    usr_id = at_to_usrid(at)
    if at:
        payload = {"qq": usr_id}
    elif username == "":
        payload = {"qq": str(event.get_user_id())}
    else:
        payload = {"username": username}
    img, success = await generate(payload)
    if success == 400:
        await matcher.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await matcher.send("该用户禁止了其他人获取数据。")
    else:
        await matcher.send(
            Message(
                [
                    MessageSegment(
                        "image",
                        {
                            "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}",
                        },
                    ),
                ],
            ),
        )


best_50_pic = on_command("b50")


@best_50_pic.handle()
async def _(event: Event, matcher: Matcher, message: Message = CommandArg()):
    username = str(message).strip()
    at = await get_message_at(event.json())
    usr_id = at_to_usrid(at)
    if at:
        payload = {"qq": usr_id, "b50": True}
    elif username == "":
        payload = {"qq": str(event.get_user_id()), "b50": True}
    else:
        payload = {"username": username, "b50": True}
    img, success = await generate50(payload)
    if success == 400:
        await matcher.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await matcher.send("该用户禁止了其他人获取数据。")
    else:
        await matcher.send(
            Message(
                [
                    MessageSegment(
                        "image",
                        {
                            "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}",
                        },
                    ),
                ],
            ),
        )


async def get_message_at(data: str) -> list:
    """
    获取at列表
    :param data: event.json()
    抄的groupmate_waifu
    """
    qq_list = []
    datas: Dict[str, Any] = json.loads(data)
    try:
        for msg in datas["message"]:
            if msg["type"] == "at":
                qq_list.append(int(msg["data"]["qq"]))
        return qq_list  # noqa: TRY300
    except Exception:
        return []


def at_to_usrid(ats: List[str]):
    """at对象变qqid否则返回usr_id"""
    if ats != []:
        at: str = ats[0]
        usr_id: str = at
        return usr_id
    return None


check_mai_data = on_command("检查mai资源", permission=SUPERUSER)
force_check_mai_data = on_command("强制检查mai资源", permission=SUPERUSER)


@check_mai_data.handle()
async def _(
    matcher: Matcher,
):
    await check_mai_data.send("正在尝试下载，大概需要2-3分钟")
    logger.info("开始检查资源")
    await matcher.send(await check_mai())


@force_check_mai_data.handle()
async def _(
    matcher: Matcher,
):
    await matcher.send("正在尝试下载，大概需要2-3分钟")
    logger.info("开始检查资源")
    await matcher.send(await check_mai(force=True))
