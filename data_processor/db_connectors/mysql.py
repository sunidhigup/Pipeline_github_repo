# import mysql.connector
# from db_connectors.settings import MYSQL

# def connect(step_param,db,table):
#     conn = mysql.connector.connect(
#         host=MYSQL.HOST,
#         user=MYSQL.USER,
#         passwd=MYSQL.PASSWORD
#     )
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM sakila.actor LIMIT 5')
#     conn.close()