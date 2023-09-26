import sqlite3
from controller.confidence_controller import ConfidenceController
from controller.view_controller import ViewController
from controller.stock_controller import StockController
from controller.database import Database, DatabaseType


class UserController(Database):
    def __init__(self):
        super().__init__('database/database_network.db', DatabaseType.sqlite)
        self.stock_controller = StockController()
        self.confidence_controller = ConfidenceController()
        self.view_controller = ViewController()

    def create_user(self, user_id: str):
        super().inserter(table='users', cols=['user_id'], vals=[user_id])

    def remove_user(self, user_id: str):
        super().deleter(table='users', cols=['user_id'], vals=[user_id])
        self.stock_controller.remove_user(user_id)

        self.view_controller.delete_person(user_id, 'pq_view')
        self.view_controller.delete_person(user_id, 'absolute_view')
        self.confidence_controller.delete_person(user_id, 'interval')
        self.confidence_controller.delete_person(user_id, 'confidences')
