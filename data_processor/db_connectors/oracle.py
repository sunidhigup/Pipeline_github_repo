# import cx_Oracle
# from db_connectors.settings import ORACLE


# def connect(step_param,db,table):
   
#     conn = cx_Oracle.connect(
#         user=ORACLE.USER, 
#         password=ORACLE.PASSWORD, 
#         dsn=ORACLE.DSN
#     )
#     c = conn.cursor()
#     c.execute('SELECT * FROM employees WHERE ROWNUM <= 10')
#     conn.close()