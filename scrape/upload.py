import pymongo
import json
from pymongo import MongoClient, InsertOne

client = pymongo.MongoClient("mongodb+srv://davenfroberg:WjxywruYe42mXrVe@nwhacks.dtnoj.mongodb.net/?retryWrites=true&w=majority&appName=nwhacks")
db = client.jobs
collection = db.labelled

with open('../OLD.json') as file:
    all_jobs = json.load(file)

requests = [InsertOne(job) for job in all_jobs]
result = collection.bulk_write(requests)

print(f'Inserted {result.inserted_count} documents')