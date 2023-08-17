import asyncio

import aiohttp
from pydantic import BaseModel

base_url = "http://api.place.fanyu.site"

async def update_pl():
    async with aiohttp.ClientSession() as session:
        urls = "http://wc.wahlap.net/maidx/rest/location"
        async with session.get(urls) as response:
            result = await response.json()
    print(result)
    return update_pl

async def get_place_count(place_id, group_id):

    params = {
        'place_id': place_id,
        'group_id': group_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(base_url, json=params) as response:
            data = await response.json()

    # 检查返回的数据
    if 'code' in data and data['code'] == 200:
        result = data['result']
        place_name = result['place_name']
        place_count = result['place_count']
        place_id = result['place_id']
        machine_count = result['machine_count']
        last_update_datetime = result['last_update_datetime']
        logs = result['logs']

        # 处理日志列表
        for log in logs:
            user_id = log['user_id']
            update_datetime = log['update_datetime']
            set_place_count = log['set_place_count']
            group_id = log['group_id']

        # 在这里进行进一步处理或返回数据
        return place_count
    else:
        # 处理错误情况
        return None
    
class BindPlaceInput(BaseModel):
    place_id: int
    group_id: int
    machine_count: int
    place_name: str
    alias_name: str
    api_key:str

class BindPlaceOutput(BaseModel):
    code: int
    result: dict

async def bind_place(input_params: BindPlaceInput) -> BindPlaceOutput:
    url = 'https://api.place.fanyu.site/bind_place' 

    data = {
        'place_id': input_params.place_id,
        'group_id': input_params.group_id,
        'machine_count': input_params.machine_count,
        'place_name': input_params.place_name,
        'alias_name': input_params.alias_name,
        'api_key':input_params.api_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
    print(result)
    output_params = BindPlaceOutput(
        code=result.get('code'),
        result=result.get('result')
    )

    return output_params

async def ex_bind():
    input_params = BindPlaceInput(
        place_id=1027,
        group_id=114514,
        machine_count=2,
        place_name='wawawa',
        alias_name='aaaa',
        api_key='LmRwE3B0tfWUS8D5TqVpPXrJzjIyYFCObN6'
    )
    output_params = await bind_place(input_params)

    if output_params.code == 200:
        place_id = output_params.result.get('place_id')
        alias_name = output_params.result.get('alias_name')

        print('绑定成功：place_id:', place_id, 'alias_name:', alias_name)
    else:
        print('绑定失败，错误代码：', output_params.code)

# asyncio.run(update_pl())
asyncio.run(ex_bind())