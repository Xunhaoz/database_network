import json

import pymongo


def create_absolute_view(user_id: str, view: str):
    try:
        view = json.loads(view)
    except Exception as e:
        return {'msg': 'Json 格式錯誤請更改後直接複製貼上'}

    try:
        if select_person(user_id, 'absolute_view'):
            update_person_view(user_id, view, 'absolute_view')
        else:
            insert_person_view(user_id, view, 'absolute_view')
    except Exception as e:
        return {'msg': '資料庫寫入失敗'}

    delete_person(user_id, 'pq_view')
    return {'msg': '絕對-觀點矩陣更新成功'}


def create_pq_view(user_id: str, view: str):
    try:
        view = json.loads(view)
        view.pop('note')
    except Exception as e:
        return {'msg': 'Json 格式錯誤請更改後直接複製貼上'}

    try:
        if select_person(user_id, 'pq_view'):
            update_person_view(user_id, view, 'pq_view')
        else:
            insert_person_view(user_id, view, 'pq_view')
    except Exception as e:
        return {'msg': '資料庫寫入失敗'}

    delete_person(user_id, 'confidences')
    delete_person(user_id, 'absolute_view')
    return {'msg': '相對觀點矩陣更新成功'}


def read_view(user_id: str) -> dict:
    pq_view = select_person(user_id, 'pq_view')
    absolute_view = select_person(user_id, 'absolute_view')
    if not pq_view and not absolute_view:
        return {'msg': '尚未設定觀點矩陣'}
    elif pq_view:
        return {'msg': json.dumps(pq_view['view'], ensure_ascii=False).replace("\\", '')}
    elif absolute_view:
        return {'msg': json.dumps(absolute_view['view'], ensure_ascii=False).replace("\\", '')}


def insert_person_view(user_id: str, view: dict, col: str):
    client = pymongo.MongoClient("localhost:27017")
    col = client['database_network'][col]
    col.insert_one({'user_id': user_id, 'view': json.dumps(view)})


def update_person_view(user_id: str, view: dict, col: str):
    client = pymongo.MongoClient("localhost:27017")
    col = client['database_network'][col]
    col.find_one_and_update(filter={'user_id': user_id}, update={"$set": {'view': json.dumps(view)}})


def select_person(user_id: str, col: str) -> dict:
    client = pymongo.MongoClient("localhost:27017")
    col = client['database_network'][col]
    x = col.find_one(filter={'user_id': user_id})
    return x


def delete_person(user_id: str, col: str):
    client = pymongo.MongoClient("localhost:27017")
    col = client['database_network'][col]
    col.delete_many(filter={'user_id': user_id})
