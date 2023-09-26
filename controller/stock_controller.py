import json
import sqlite3
import pathlib
import yfinance as yf

from controller.database import Database, DatabaseType


class StockController(Database):
    def __init__(self):
        super().__init__('database/database_network.db', DatabaseType.sqlite)

    def create_stock(self, user_id: str, stock_id: str) -> dict:
        if super().selector(table='stock', cols=['user_id', 'stock_id'], vals=[user_id, stock_id]):
            res = {'msg': "此檔股票已存在於關注清單"}
            return res

        if super().selector(table='stock', cols=['stock_id'], vals=[stock_id]):
            super().inserter(
                table='stock',
                cols=['user_id', 'stock_id', 'stock_path'],
                vals=[user_id, stock_id, f'static/stocks/{stock_id}.csv']
            )
            res = {'msg': "新增關注清單成功"}
            return res

        df = yf.download(stock_id, period="max")
        if len(df) == 0:
            res = {'msg': "股票代碼不存在"}
            return res

        df.to_csv(f"static/stocks/{stock_id}.csv")
        super().inserter(
            table='stock',
            cols=['user_id', 'stock_id', 'stock_path'],
            vals=[user_id, stock_id, f'static/stocks/{stock_id}.csv']
        )
        res = {'msg': "新增關注清單成功"}
        return res

    def remove_user(self, user_id: str):
        result = super().selector(table='stock', cols=['user_id'], vals=[user_id])
        for res in result:
            super().deleter(table='stock', cols=['user_id', 'stock_id'], vals=[res[1], res[2]])

    def remove_stock(self, user_id: str, stock_id: str) -> dict:
        result = super().selector(table='stock', cols=['user_id', 'stock_id'], vals=[user_id, stock_id])
        if not result:
            res = {'msg': "刪除關注清單成功"}
            return res

        super().deleter(table='stock', cols=['user_id', 'stock_id'], vals=[user_id, stock_id])
        stock_path = result[0][3]
        if not super().selector(table='stock', cols=['stock_id'], vals=[stock_id]):
            try:
                pathlib.Path(stock_path).unlink()
            except Exception as e:
                pass
            res = {'msg': "刪除關注清單成功"}
            return res

        res = {'msg': "刪除關注清單成功"}
        return res

    def read_stock(self, user_id: str) -> dict:
        result = super().selector(table='stock', cols=['user_id'], vals=[user_id])
        if not result:
            res = {'msg': "關注清單目前為空"}
            return res
        result = [_[2] for _ in result]
        res = {'msg': "關注清單：\n" + '\n'.join(result)}
        return res

    def template_absolute_view(self, user_id: str) -> dict:
        result = super().selector(table='stock', cols=['user_id'], vals=[user_id])
        if not result:
            res = {'msg': "關注清單目前為空"}
            return res

        result = {_[2]: 0.0 for _ in result}
        res = {'msg': "@觀點矩陣-絕對輸入\n" + json.dumps(result, ensure_ascii=False)}
        return res

    def template_pq_view(self, user_id: str, msg: str) -> dict:
        result = super().selector(table='stock', cols=['user_id'], vals=[user_id])
        if not result:
            res = {'msg': "關注清單目前為空"}
            return res

        try:
            msg = int(msg)
        except Exception as e:
            res = {'msg': "觀點因子必須為整數"}
            return res

        template = {
            "Q": [0.0] * msg,
            "P": [[0.0] * len(result) for _ in range(msg)],
            "note": "設定參數可以參考 https://pyportfolioopt.readthedocs.io/en/latest/BlackLitterman.html#views 文件內容"
        }
        res = {'msg': "@觀點矩陣-相對輸入\n" + json.dumps(template, ensure_ascii=False)}
        return res

    def template_confidences(self, user_id: str):
        result = super().selector(table='stock', cols=['user_id'], vals=[user_id])
        if not result:
            res = {'msg': "關注清單目前為空"}
            return res

        result = {'confidences': [0.5] * len(result)}
        res = {'msg': "@置信矩陣-輸入\n" + json.dumps(result, ensure_ascii=False)}
        return res

    def template_interval(self, user_id: str):
        result = super().selector(table='stock', cols=['user_id'], vals=[user_id])
        if not result:
            res = {'msg': "關注清單目前為空"}
            return res

        result = {'intervals': [[0.0, 0.0] for _ in result]}
        res = {'msg': "@置信區間-輸入\n" + json.dumps(result, ensure_ascii=False)}
        return res
