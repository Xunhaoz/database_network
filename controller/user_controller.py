import sqlite3
import controller.stock_controller as stock_controller
import controller.confidence_controller as confidence_controller
import controller.view_controller as view_controller


def create_user(user_id: str):
    insert_person(user_id)


def remove_user(user_id: str):
    delete_person(user_id)
    stock_controller.remove_user(user_id)
    view_controller.delete_person(user_id, 'pq_view')
    view_controller.delete_person(user_id, 'absolute_view')
    confidence_controller.delete_person(user_id, 'interval')
    confidence_controller.delete_person(user_id, 'confidences')


def insert_person(user_id: str):
    conn = sqlite3.connect('database/database_network.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


def delete_person(user_id: str):
    conn = sqlite3.connect('database/database_network.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
