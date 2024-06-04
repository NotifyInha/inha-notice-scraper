import aiohttp
from DataModel import Notice, NoticeCreate, NoticeGet
from utils.DatabaseWrapper import DatabaseWrapper
from urllib import parse
from Config import server_address

class BackendWrapper(DatabaseWrapper):
    def __init__(self):
        pass

    async def ping(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(server_address + "/api") as response:
                return response.status == 200

    async def check_data(self, data: Notice) -> bool:
        endpoint = server_address + '/v1/notices'
        param = parse.urlencode({'url': data.url})
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, params=param) as response:
                res = await response.json()
                if len(res['items']) == 0:
                    return False
                res: dict = res['items'][0]
                res['_id'] = res.pop("id")
                return NoticeGet(**res)

    async def insert(self, data: NoticeCreate):
        endpoint = server_address + '/v1/notices'
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, data=data.model_dump_json(),headers={'Content-Type': 'application/json'}) as response:
                return response.status

    async def update(self, data: NoticeCreate):
        endpoint = server_address + f'/v1/notices/{data.id}'
        async with aiohttp.ClientSession() as session:
            async with session.put(endpoint, data=data.model_dump_json(),headers={'Content-Type': 'application/json'}) as response:
                return response.status

    async def upload(self, data: Notice):
        items: NoticeGet = await self.check_data(data)
        if items is False:
            res = await self.insert(data)
            if res == 409:
                return False
            return True
        else:
            data.id = items.id
            res = await self.update(data)
            if res == 200:
                return data
            elif res == 409:
                return False