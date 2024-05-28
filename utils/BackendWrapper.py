import requests
from DataModel import Notice, NoticeLight
from utils.DatabaseWrapper import DatabaseWrapper
from urllib import parse
from Config import server_address


class BackendWrapper(DatabaseWrapper):
    def __init__(self):
        pass

    def ping(self) -> bool:
        request = requests.get(server_address)
        return request.status_code == 200

    def check_data(self, data:Notice) -> bool:
        endpoint = server_address + '/v1/notices'
        param = parse.urlencode({'url': data.url})
        response = requests.get(endpoint, params=param)
        res = response.json()
        if len(res['items']) == 0:
            return False
        res:dict = res['items'][0]
        res['_id'] = res.pop("id")
        return NoticeLight(**res)

    def insert(self, data: Notice):
        endpoint = server_address + '/v1/notices'
        response = requests.post(endpoint, json=data.to_dict())
        return response.status_code
    
    def update(self, data: Notice):
        endpoint = server_address + f'/v1/notices/{data.id}'
        response = requests.put(endpoint, json=data.to_dict())
        return response.status_code

    def upload(self, data:Notice):
        items:NoticeLight = self.check_data(data)
        if items is False:
            res = self.insert(data)
            if res == 409:
                return False
            return True
        else:
            data.id = items.id
            res = self.update(data)
            if res == 200:
                return data
            elif res == 409:
                return False
            


    