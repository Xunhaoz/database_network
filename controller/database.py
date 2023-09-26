from enum import Enum
import sqlite3
import pymongo


class DatabaseType(Enum):
    sqlite = 'sqlite'
    mongo = 'mongo'


class Database:
    def __init__(self, database_url: str, database_type: DatabaseType):
        self.database_url = database_url
        self.database_type = database_type

        if self.database_type == DatabaseType.sqlite:
            self.conn = sqlite3.connect(self.database_url)
            self.cursor = self.conn.cursor()
        elif self.database_type == DatabaseType.mongo:
            self.conn = pymongo.MongoClient(self.database_url)['database_network']
        else:
            self.conn = ""

    def selector(self, **kwargs) -> list or dict:
        result = []
        if self.database_type == DatabaseType.sqlite:
            sql = f"SELECT * FROM {kwargs['table']} WHERE {' AND '.join([k + '=?' for k in kwargs['cols']])}"
            self.cursor.execute(sql, kwargs['vals'])
            result = self.cursor.fetchall()

        elif self.database_type == DatabaseType.mongo:
            result = self.conn[kwargs['table']].find(filter={x: y for x, y in zip(kwargs['cols'], kwargs['vals'])})
            result = list(result)

        return result

    def updater(self, **kwargs) -> None:
        if self.database_type == DatabaseType.sqlite:
            sql = f"UPDATE {kwargs['table']} SET {', '.join([k + '=?' for k in kwargs['u_cols']])} WHERE {' AND '.join([k + '=?' for k in kwargs['cols']])}"
            self.cursor.execute(sql, kwargs['u_vals'] + kwargs['vals'])

        elif self.database_type == DatabaseType.mongo:
            self.conn[kwargs['table']].find_one_and_update(
                filter={x: y for x, y in zip(kwargs['cols'], kwargs['vals'])},
                update={"$set": {x: y for x, y in zip(kwargs['u_cols'], kwargs['u_vals'])}})

    def deleter(self, **kwargs) -> None:
        if self.database_type == DatabaseType.sqlite:
            sql = f"DELETE FROM {kwargs['table']} WHERE {' AND '.join([k + '=?' for k in kwargs['cols']])}"
            self.cursor.execute(sql, kwargs['vals'])
            self.conn.commit()

        elif self.database_type == DatabaseType.mongo:
            self.conn[kwargs['table']].delete_many(filter={x: y for x, y in zip(kwargs['cols'], kwargs['vals'])})

    def inserter(self, **kwargs) -> None:
        if self.database_type == DatabaseType.sqlite:
            sql = f"INSERT INTO {kwargs['table']} ({', '.join(kwargs['cols'])}) VALUES ({', '.join(['?' for _ in kwargs['cols']])})"
            self.cursor.execute(sql, kwargs['vals'])
            self.conn.commit()

        elif self.database_type == DatabaseType.mongo:
            self.conn[kwargs['table']].insert_one({x: y for x, y in zip(kwargs['cols'], kwargs['vals'])})
