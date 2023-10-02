import json

import pymongo
from controller.database import Database, DatabaseType


class ConfidenceController(Database):
    def __init__(self):
        super().__init__('localhost:27017', DatabaseType.mongo)

    def create_confidences(self, user_id: str, confidence: str):
        try:
            confidence = json.loads(confidence)
        except Exception as e:
            return {'msg': 'Json 格式錯誤請更改後直接複製貼上'}

        try:
            if super().selector(table='confidences', cols=['user_id'], vals=[user_id]):
                print(confidence)
                super().updater(
                    table='confidences', cols=['user_id'],
                    vals=[user_id], u_cols=['confidence'], u_vals=[confidence]
                )
            else:
                super().inserter(table='confidences', cols=['user_id', 'confidence'], vals=[user_id, confidence])
        except Exception as e:
            return {'msg': '資料庫寫入失敗'}

        super().deleter(table='pq_view', cols=['user_id'], vals=[user_id])
        super().deleter(table='interval', cols=['user_id'], vals=[user_id])
        return {'msg': '置信矩陣更新成功'}

    def read_confidences(self, user_id: str) -> dict:
        confidences = super().selector(table='confidences', cols=['user_id'], vals=[user_id])[0]
        if not confidences:
            return {'msg': '尚未設定置信矩陣'}
        elif confidences:
            return {'msg': json.dumps(confidences['confidence'], ensure_ascii=False).replace("\\", '')}

    def create_interval(self, user_id: str, confidence: str) -> dict:
        try:
            confidence = json.loads(confidence)
        except Exception as e:
            return {'msg': 'Json 格式錯誤請更改後直接複製貼上'}

        try:
            if super().selector(table='interval', cols=['user_id'], vals=[user_id]):
                super().updater(
                    table='interval', cols=['user_id'],
                    vals=[user_id], u_cols=['confidence'], u_vals=[confidence]
                )
            else:
                super().inserter(table='interval', cols=['user_id', 'confidence'], vals=[user_id, confidence])
        except Exception as e:
            return {'msg': '資料庫寫入失敗'}

        super().deleter(table='pq_view', cols=['user_id'], vals=[user_id])
        super().deleter(table='confidences', cols=['user_id'], vals=[user_id])
        return {'msg': '置信區間更新成功'}

    def read_interval(self, user_id: str) -> dict:
        confidences = super().selector(table='interval', cols=['user_id'], vals=[user_id])
        if not confidences:
            return {'msg': '尚未設定置信區間'}
        elif confidences:
            return {'msg': json.dumps(confidences['confidences'], ensure_ascii=False).replace("\\", '')}

    def delete_person(self, user_id: str, table: str) -> None:
        super().deleter(table=table, cols=['user_id'], vals=[user_id])
