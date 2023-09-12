import json

import pymongo


def create_confidences(user_id: str, confidence: str):
    try:
        confidence = json.loads(confidence)
    except Exception as e:
        return {'msg': 'Json 格式錯誤請更改後直接複製貼上'}

    try:
        if select_person(user_id, 'confidences'):
            update_person_confidence(user_id, confidence, 'confidences')
        else:
            insert_person_confidence(user_id, confidence, 'confidences')
    except Exception as e:
        return {'msg': '資料庫寫入失敗'}

    delete_person(user_id, 'pq_view')
    delete_person(user_id, 'interval')
    return {'msg': '置信矩陣更新成功'}


def read_confidences(user_id: str) -> dict:
    confidences = select_person(user_id, 'confidences')
    if not confidences:
        return {'msg': '尚未設定置信矩陣'}
    elif confidences:
        return {'msg': json.dumps(confidences['confidences'], ensure_ascii=False).replace("\\", '')}


def create_interval(user_id: str, confidence: str) -> dict:
    try:
        confidence = json.loads(confidence)
    except Exception as e:
        return {'msg': 'Json 格式錯誤請更改後直接複製貼上'}

    try:
        if select_person(user_id, 'interval'):
            update_person_confidence(user_id, confidence, 'interval')
        else:
            insert_person_confidence(user_id, confidence, 'interval')
    except Exception as e:
        return {'msg': '資料庫寫入失敗'}

    delete_person(user_id, 'pq_view')
    delete_person(user_id, 'confidences')
    return {'msg': '置信區間更新成功'}


def read_interval(user_id: str) -> dict:
    confidences = select_person(user_id, 'interval')
    if not confidences:
        return {'msg': '尚未設定置信區間'}
    elif confidences:
        return {'msg': json.dumps(confidences['confidences'], ensure_ascii=False).replace("\\", '')}


def insert_person_confidence(user_id: str, view: dict, col: str):
    client = pymongo.MongoClient("localhost:27017")
    col = client['database_network'][col]
    col.insert_one({'user_id': user_id, 'confidences': json.dumps(view)})


def update_person_confidence(user_id: str, view: dict, col: str):
    client = pymongo.MongoClient("localhost:27017")
    col = client['database_network'][col]
    col.find_one_and_update(filter={'user_id': user_id}, update={"$set": {'confidences': json.dumps(view)}})


def select_person(user_id: str, col: str) -> dict:
    client = pymongo.MongoClient("localhost:27017")
    col = client['database_network'][col]
    x = col.find_one(filter={'user_id': user_id})
    return x


def delete_person(user_id: str, col: str):
    client = pymongo.MongoClient("localhost:27017")
    col = client['database_network'][col]
    col.delete_many(filter={'user_id': user_id})
