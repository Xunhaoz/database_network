def test(**kwargs):
    sql = f"INSERT INTO {kwargs['table']} ({', '.join(kwargs['cols'])}) VALUES ({', '.join(['?' for _ in kwargs['cols']])})"
    print(kwargs['vals'])
    print(sql)


test(table='stock', cols=['user_id', 'stock_id'], vals=['user_id', 'stock_id'])
