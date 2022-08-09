from boto3.dynamodb.conditions import Attr

from Boto3_client.dynamo_writer import get_dynamodb
from constant import Constant
from constant.Constant import preprocessor_constants
from extract import extract
from logger.cloudwatch.log_utils import log_initiator
from logger.cloudwatch.log_utils import write_logs

# Reading AWS Creadentials
AWS_CREDENTIALS = Constant.AWS_CREDENTIALS
dynamodb = get_dynamodb()


def process(meta_data):
    """
    Perform operation on files based on their extension
    :param meta_data:
    :param table_name:
    """

    # Writing logs
    write_logs(preprocessor_constants.INFO, preprocessor_constants.INFO_START)

    # Checking for zip extension
    if meta_data["extension"] == "zip":  # check for ".zip" extension

        write_logs(preprocessor_constants.INFO, preprocessor_constants.INFO_ZIP)
        try:
            extract(meta_data)
            write_logs(preprocessor_constants.INFO, preprocessor_constants.INFO_EXT)
        except:
            

            write_logs(preprocessor_constants.INFO, preprocessor_constants.INFO_ERROR)
            
            meta_data["Status"] = "Failed"
            dynamodb.Table(Constant.STATUS_TABLE_NAME).put_item(Item=meta_data)

            # try:
            #     #decrypt(client_name,output_folder,config)
            #     write_logs("Info", "[******* Decryption successful *********]")
            # except:

            #     write_logs("Info", "[******* Error caught during decryption *********]")


if __name__ == "__main__":

    table_name = Constant.STATUS_TABLE_NAME
    file_classification_table = Constant.FILE_TABLE
    dynamo_meta_response = dynamodb.Table(table_name).scan(FilterExpression=Attr('Status').eq('Pending'))

    stream_name = dynamo_meta_response[preprocessor_constants.ITEMS][0]["id"]
    log_initiator(stream_name)

    for item in dynamo_meta_response[preprocessor_constants.ITEMS]:
        
        process(item)
