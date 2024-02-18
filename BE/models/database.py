# models.py

from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

load_dotenv()  # 환경 변수 로드
ca = certifi.where()

class Database:
    def __init__(self):
        MONGO_URI = os.getenv("MONGO_URI")
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        self.buyerDB = client.buyer.search_result
        self.archiveDB = client.archive.user01

    def insert_archive(self, data):
        self.archiveDB.insert_many(data)

    def clear_archive(self):
        self.archiveDB.delete_many({})

    def get_buyers(self):
        return self.buyerDB.find()