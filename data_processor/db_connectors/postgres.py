from data_processor.db_connectors.settings import POSTGRES
# from settings import POSTGRES
import psycopg2
from data_processor.logging.cloudwatch.log_utils import write_logs

def connect(step_param,db,table ):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

  # connect to the PostgreSQL server
        conn = psycopg2.connect(host=POSTGRES.HOST,database=POSTGRES.DATABASE,
                                    user=POSTGRES.USER,password=POSTGRES.PASSWORD)
    
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM "%s"."%s"',(eval(db),eval(table)))
        # cur.execute('SELECT * FROM "Financial"."ApplicantData"')

        data = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = step_param.spark.createDataFrame(data,colnames)
        # close the communication with the PostgreSQL
        cur.close()
        return df
    except (Exception, psycopg2.DatabaseError) as e:
        write_logs("ERROR", "ERROR CAUGHT - {}".format(str(e)))
        raise e