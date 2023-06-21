import pymysql

# Настройки соединения с базой данных
HOST = 'localhost'
USER = 'root'
PASSWORD = 'root'
DATABASE = 'grants_s11'
PORT = 3306

# Создание соединения с базой данных
connection = pymysql.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    port=PORT,
    database=DATABASE,
    cursorclass=pymysql.cursors.DictCursor
)