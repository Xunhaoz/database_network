import json

from controller.database import Database, DatabaseType


class ViewController(Database):
    def __init__(self):
        super().__init__('localhost:27017', DatabaseType.mongo)

    def create_absolute_view(self, user_id: str, view: str):
        try:
            view = json.loads(view)
        except Exception as e:
            return {'msg': 'Json 格式錯誤請更改後直接複製貼上'}

        try:

            if super().selector(table='absolute_view', cols=['user_id'], vals=[user_id]):
                super().updater(table='absolute_view', cols=['user_id'], vals=[user_id], u_cols=['view'], u_vals=[view])
            else:
                super().inserter(table='absolute_view', cols=['user_id', 'view'], vals=[user_id, view])
        except Exception as e:
            return {'msg': '資料庫寫入失敗'}

        super().deleter(table='absolute_view', cols=['user_id'], vals=[user_id])
        return {'msg': '絕對-觀點矩陣更新成功'}

    def create_pq_view(self, user_id: str, view: str):
        try:
            view = json.loads(view)
            view.pop('note')
        except Exception as e:
            return {'msg': 'Json 格式錯誤請更改後直接複製貼上'}

        try:
            if super().selector(table='pq_view', cols=['user_id'], vals=[user_id]):
                super().updater(table='pq_view', cols=['user_id'], vals=[user_id], u_cols=['view'], u_vals=[view])
            else:
                super().inserter(table='pq_view', cols=['user_id', 'view'], vals=[user_id, view])
        except Exception as e:
            return {'msg': '資料庫寫入失敗'}

        super().deleter(table='confidences', cols=['user_id'], vals=[user_id])
        super().deleter(table='absolute_view', cols=['user_id'], vals=[user_id])
        super().deleter(table='interval', cols=['user_id'], vals=[user_id])
        return {'msg': '相對觀點矩陣更新成功'}

    def read_view(self, user_id: str) -> dict:
        pq_view = super().selector(table='pq_view', cols=['user_id'], vals=[user_id])
        absolute_view = super().selector(table='absolute_view', cols=['user_id'], vals=[user_id])
        if not pq_view and not absolute_view:
            return {'msg': '尚未設定觀點矩陣'}
        elif pq_view:
            return {'msg': json.dumps(pq_view['view'], ensure_ascii=False).replace("\\", '')}
        elif absolute_view:
            return {'msg': json.dumps(absolute_view['view'], ensure_ascii=False).replace("\\", '')}

    def delete_person(self, user_id: str, table: str) -> None:
        super().deleter(table=table, cols=['user_id'], vals=[user_id])
