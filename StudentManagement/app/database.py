import pymongo

class DB(object):
    url="mongodb://localhost:27017/"

    @staticmethod
    def init():
        client=pymongo.MongoClient(DB.url)
        DB.DATABASE=client['StudentManagement']
    
    @staticmethod
    def insert(collection, data):
        return DB.DATABASE[collection].insert(data)

    @staticmethod
    def find_one(collection,query):
        return DB.DATABASE[collection].find_one(query)

    @staticmethod
    def find_many(collection,query):
        return DB.DATABASE[collection].find(query)
        
    @staticmethod
    def update_one(collection,query,newval):
        return DB.DATABASE[collection].update(query,newval)

    @staticmethod
    def showall(collection):
        mydoc=DB.DATABASE[collection].aggregate([{'$lookup':{'from':'PersonalInfo','localField':'Email','foreignField':'Email','as':'fromItems'}},{'$replaceRoot':{'newRoot':{'$mergeObjects':[{'$arrayElemAt':['$fromItems',0]},"$$ROOT"]}}},{'$project':{'fromItems':0}}])
        return mydoc