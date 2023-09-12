import sqlite3

conn = sqlite3.connect('database_network.db')

c = conn.cursor()
c.execute('''
    CREATE TABLE users
    (user_id VARCHAR PRIMARY KEY,
    q1 INTEGER DEFAULT 0,
    q2 INTEGER DEFAULT 0,
    q3 INTEGER DEFAULT 0,
    q4 INTEGER DEFAULT 0,
    q5 INTEGER DEFAULT 0,
    q6 INTEGER DEFAULT 0,
    q7 INTEGER DEFAULT 0,
    q8 INTEGER DEFAULT 0,
    q9 INTEGER DEFAULT 0)
''')

c.execute('''
    CREATE TABLE stock
    (id integer primary key autoincrement,
    user_id VARCHAR,
    stock_id VARCHAR,
    stock_path VARCHAR)
''')

conn.commit()
conn.close()
