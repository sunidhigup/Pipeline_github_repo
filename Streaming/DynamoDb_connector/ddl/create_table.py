from DynamoDb_connector.ddl.init import get_dynamodb
from DynamoDb_connector.settings import Settings

Dynamo_Table= Settings.DYNAMO

def createTableIfNotExists():
    '''
    Create a DynamoDB table if it does not exist.
    This must be run on the Spark driver, and not inside foreach.
    '''
    #Getting dynamoDb instance
    dynamodb = get_dynamodb()

    #Creating table
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    for table_name in Dynamo_Table:
        if table_name not in existing_tables:
            table = dynamodb.create_table(
          TableName=table_name,
          KeySchema=[{'AttributeName': 'stream_name', 'KeyType': 'HASH'}],
          AttributeDefinitions=[
              {'AttributeName': 'stream_name', 'AttributeType': 'String'}],
          ProvisionedThroughput={
              'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
             )
