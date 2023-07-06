from pymongo import MongoClient
conn = MongoClient("mongodb://localhost:27017/")
nuovodb = conn["goldapi"]
colle = nuovodb["xau"]

def print_db():
    for x in colle.find():
        print(x)
        return x