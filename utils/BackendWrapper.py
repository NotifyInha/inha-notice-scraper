import aiohttp
from DataModel import Notice, NoticeLight
from utils.DatabaseWrapper import DatabaseWrapper
from urllib import parse
from Config import server_address

class BackendWrapper(DatabaseWrapper):
    def __init__(self):
        pass

    async def ping(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(server_address) as response:
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
                return NoticeLight(**res)

    async def insert(self, data: Notice):
        endpoint = server_address + '/v1/notices'
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=data.to_dict()) as response:
                return response.status

    async def update(self, data: Notice):
        endpoint = server_address + f'/v1/notices/{data.id}'
        async with aiohttp.ClientSession() as session:
            async with session.put(endpoint, json=data.to_dict()) as response:
                return response.status

    async def upload(self, data: Notice):
        items: NoticeLight = await self.check_data(data)
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