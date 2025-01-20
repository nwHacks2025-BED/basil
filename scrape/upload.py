import pymongo
import json
from pymongo import MongoClient, InsertOne

with open('../config.json') as config_file:
    config = json.load(config_file)
    uri = config["connectionString"]

client = pymongo.MongoClient(uri)
db = client.jobs
collection = db.labelled

with open('../OLD.json') as file:
    all_jobs = json.load(file)

requests = [InsertOne(job) for job in all_jobs]
result = collection.bulk_write(requests)

print(f'Inserted {result.inserted_count} documents')