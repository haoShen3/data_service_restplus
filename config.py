from pymongo import MongoClient

class mlab():
    def __init__(self, DB_HOST, DB_PORT):
        self.DB_HOST = DB_HOST
        self.DB_PORT = DB_PORT

    def createClient(self):
        return MongoClient(self.DB_HOST, self.DB_PORT)
