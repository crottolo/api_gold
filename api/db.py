import pymongo
import datetime
conn = pymongo.MongoClient("mongodb://localhost:27017/")
db = conn["goldapi"]
colle = db["xau"]


def connectdb():
    try:
        conn = pymongo.MongoClient("mongodb://localhost:27017/")
        if 'goldapi' in conn.list_database_names():
            print("Database exists!")
        else:
            
            insert = colle.insert_one({})
            delete_insert = colle.delete_one({"_id": insert.inserted_id})
            print("Collection created!")
    except Exception as e:
        print(e)
        
def insert_data():
    try:
        insert = colle.insert_one({"name": "xau", "price": 1000})
        print(insert.inserted_id)
        
        total_rows = colle.count_documents({})
        print   (total_rows)
        
    except Exception as e:
        print(e)
# try:
#     insert = colle.insert_one({"name": "xau", "price": 1000})
#     print(insert.inserted_id)
    
#     total_rows = colle.count_documents({})
#     print   (total_rows)
    
# except Exception as e:
#     print(e)

if __name__ == '__main__':
    connectdb()
    insert_data()


