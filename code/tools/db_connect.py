from pymongo import MongoClient


def get_collection(conn_detail: list):
    db_cred, db, collection = conn_detail
    with open(db_cred, 'r', encoding='utf-8') as fhand:
        uri = fhand.read().strip()
        return MongoClient(uri)[db][collection]

