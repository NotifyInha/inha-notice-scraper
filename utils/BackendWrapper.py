from utils.DatabaseWrapper import DatabaseWrapper

class BackendWrapper(DatabaseWrapper):
    def __init__(self):
        pass

    def ping(self) -> bool:
        return False

    def upload(self, data):
        pass
    