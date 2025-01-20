from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
import json
ca = certifi.where()

with open('../config.json') as config_file:
    config = json.load(config_file)
    uri = config["connectionString"]

# Create a new client and connect to the server
MongoClient()
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=ca)
database = client["jobs"]


def close_connection():
    client.close()


# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)