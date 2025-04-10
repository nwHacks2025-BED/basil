from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
import json
import os
ca = certifi.where()

config_path = os.path.join(os.path.dirname(__file__), '../../config.json')
with open(config_path) as config_file:
    config = json.load(config_file)
    uri = config["connectionString"]

MongoClient()
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=ca)
database = client["jobs"]


def close_connection():
    client.close()

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)