from DynamoDb_connector.ddl.init import get_dynamodb
from DynamoDb_connector.settings import Settings


Stream_table = Settings.DYNAMO["streaming_table"]

def write_to_meta(table_name, dict):
    """Write to Dynamodb

    Args:
        table_name (string): name of table
        dict (dictionary): data to write on table
    """    
    # dict["timestamp"]=ts
    dynamodb= get_dynamodb()
    #Putting meta data into dynamoDb
    dynamodb.Table(table_name).put_item(Item=dict) 

class SendToDynamoDB_ForeachWriter:
  """
   Writes spark streaming df to DynamoDb table 
  """  
  
  def open(self, partition_id, epoch_id):
    """

    :param partition_id:
    :param epoch_id:
    :return:
    """
    # This is called first when preparing to send multiple rows.
    # Put all the initialization code inside open() so that a fresh
    # copy of this class is initialized in the executor where open()
    # will be called.
    self.dynamodb = get_dynamodb()
    return True

  def process(self, row):
    """

    :param row:
    """
    # This is called for each row after open() has been called.
    # This implementation sends one row at a time.
    # For further enhancements, contact the Spark+DynamoDB connector
    self.dynamodb.Table(Stream_table).put_item(
        Item = {})

  def close(self, err):
    """

    :param err:
    """
    # This is called after all the rows have been processed.
    if err:
      raise err
