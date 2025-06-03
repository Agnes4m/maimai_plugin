import asyncio
import json
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlencode

import aiohttp
from nonebot import on_command
from nonebot.adapters import Event, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from pydantic import BaseModel

from .libraries.tool import STATIC

base_url = "http://api.place.fanyu.site"


bind_site = on_command("maibind", aliases={"绑定机厅"}, priority=5, block=True)
show_all = on_command("maicheck", aliases={"查卡"}, priority=5, block=True)


@bind_site.handle()
async def _(matcher: Matcher, event: Event, arg: Message = CommandArg()):
    usr_id = event.get_user_id()
    msgs = arg.extract_plain_text()
    msg_list = msgs.split()
    if len(msg_list) == 1:
        msg = msg_list[0]
        alias_name = ""
    elif len(msg_list) == 2:
        alias_name = msg_list[-1]
        msg = msg_list[0]
    else:
        await matcher.finish("参数错误，应当为1-2个参数")
        return
    try:
        with (
            Path(STATIC)
            .parent.joinpath("site.json")
            .open(
                mode="r",
                encoding="utf-8",
            ) as f
        ):
            data_site: List[Dict[str, str]] = json.loads(f.read())
    except Exception:
        data_site = []
    this_site = {}
    for one_site in data_site:
        if msg in one_site["arcadeName"] or msg in one_site["id"]:
            this_site = one_site
            break
    if not this_site:
        await matcher.finish("未找到机厅，请输入微信小程序所显示机厅名称或者id")

    output_params = await bind_place(
        BindPlaceInput(
            place_id=int(this_site["placeId"]),
            group_id=114514,
            machine_count=int(this_site["machineCount"]),
            place_name=this_site["arcadeName"],
            alias_name=alias_name if alias_name else this_site["arcadeName"],
            api_key="LmRwE3B0tfWUS8D5TqVpPXrJzjIyYFCObN6",
        ),
    )
    print(output_params)
    if output_params["code"] == 200:
        place_id = output_params.get("place_id")
        alias_name = output_params.get("alias_name")
        result = output_params.get("result")
        await matcher.send(f"{result}：place_id:{place_id},alias_name:, {alias_name}")
    else:
        result = output_params.get("result")
        await matcher.send(f"{result}")
    try:
        with (
            Path(STATIC)
            .parent.joinpath("player.json")
            .open(
                "r",
                encoding="utf-8",
            ) as f
        ):
            player_json: Dict[str, List[str]] = json.loads(f.read())
    except Exception:
        player_json = {}
    if usr_id in player_json:
        player_json[usr_id].append(this_site["placeId"])
    else:
        player_json[usr_id] = [this_site["placeId"]]
    with Path(STATIC).parent.joinpath("player.json").open("w", encoding="utf-8") as f:
        json.dump(player_json, f, ensure_ascii=False)


@show_all.handle()
async def _(
    matcher: Matcher,
    event: Event,
):
    usr_id = event.get_user_id()
    try:
        with (
            Path(STATIC)
            .parent.joinpath("player.json")
            .open(
                "r",
                encoding="utf-8",
            ) as f
        ):
            player_json: Dict[str, List[str]] = json.loads(f.read())
    except Exception:
        player_json = {}
    site_list = player_json.get(usr_id)
    if site_list is None:
        await matcher.finish("用户暂未绑定")
        return
    send_msg = ""
    for one_site_id in site_list:
        msg_data = await get_place_count(
            GetPlaceCountInput(
                place_id=int(one_site_id),
                group_id=114514,
                api_key="LmRwE3B0tfWUS8D5TqVpPXrJzjIyYFCObN6",
            ),
        )
        send_msg += f"【{msg_data.place_count}人 | {msg_data.machine_count}机】| {msg_data.place_name} 最后更新：{msg_data.last_update_datetime}/n"
    await matcher.finish(send_msg)


async def update_pl():
    async with aiohttp.ClientSession() as session:
        urls = "http://wc.wahlap.net/maidx/rest/location"
        async with session.get(urls) as response:
            result = await response.json()
    if result:
        with (
            Path(STATIC)
            .parent.joinpath("site.json")
            .open(
                mode="w",
                encoding="utf-8",
            ) as f
        ):
            json.dump(result, f, ensure_ascii=False)


class BindPlaceInput(BaseModel):
    place_id: int
    group_id: int
    machine_count: int
    place_name: str
    alias_name: str
    api_key: str


async def bind_place(input_params: BindPlaceInput) -> dict:
    bind_url = f"{base_url}/bind_place"
    query_params = {
        "place_id": input_params.place_id,
        "group_id": input_params.group_id,
        "machine_count": input_params.machine_count,
        "place_name": input_params.place_name,
        "alias_name": input_params.alias_name,
        "api_key": input_params.api_key,
    }
    url = f"{bind_url}?{urlencode(query_params)}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result: Dict[str, str] = await response.json()
        print(result)
        # result = json.loads(result)
    return {"code": result.get("code"), "result": result.get("result")}


async def ex_bind():
    input_params = BindPlaceInput(
        place_id=1027,
        group_id=114514,
        machine_count=2,
        place_name="wawawa",
        alias_name="aaaa",
        api_key="LmRwE3B0tfWUS8D5TqVpPXrJzjIyYFCObN6",
    )
    await bind_place(input_params)

    # if output_params["code"] == 200:
    #     place_id = output_params["result"].get('place_id')
    #     alias_name = output_params.result.get('alias_name')
    #     print('绑定成功：place_id:', place_id, 'alias_name:', alias_name)
    # else:
    #     print('绑定失败，错误代码：', output_params["code"])


class GetPlaceCountInput(BaseModel):
    place_id: int
    group_id: int
    api_key: str


class Log(BaseModel):
    user_id: str
    update_datetime: str
    set_place_count: int
    group_id: int


class GetPlaceCountOutput(BaseModel):
    code: int
    result: str
    place_name: str
    place_count: int
    place_id: int
    machine_count: int
    last_update_datetime: str
    logs: List[Log]


async def get_place_count(input_params: GetPlaceCountInput) -> GetPlaceCountOutput:
    get_url = f"{base_url}/get_place_count"

    params = {
        "place_id": input_params.place_id,
        "group_id": input_params.group_id,
        "api_key": input_params.api_key,
    }
    url = f"{get_url}?{urlencode(params)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data: dict = await response.json()
    # data = response.json()
    print(data)
    logs = []
    for log_data in data["logs"]:
        log = Log(
            user_id=log_data["user_id"],
            update_datetime=log_data["update_datetime"],
            set_place_count=log_data["set_place_count"],
            group_id=log_data["group_id"],
        )
        logs.append(log)

    return GetPlaceCountOutput(
        code=data["code"],
        result=data["result"],
        place_name=data["place_name"],
        place_count=data["place_count"],
        place_id=data["place_id"],
        machine_count=data["machine_count"],
        last_update_datetime=data["last_update_datetime"],
        logs=logs,
    )


# asyncio.run(update_pl())
if __name__ == "__main__":
    asyncio.run(ex_bind())
