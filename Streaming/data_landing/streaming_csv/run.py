from asyncore import read
from kinesis import Kinesis
from constant.constant import Input
from source_file_reader import SourceData
import json
import time
from Streaming.env_fetcher import read_config

def main():
    """

    """
    config_data = read_config("dev","depconfig","Streaming/Config/config.json")
    # with open("config/config_stream.json", "r") as f:
    #     config_data = json.load(f)

    source = SourceData(source_path=Input.INPUT_SRC_FILE_PATH)
    source_reader = source.read_data()
    #putting data in stream
    kinesis = Kinesis(config_data["region"], config_data["Kinesis_Data_Stream"])

    
    records = source.chunkit([{"PartitionKey":config_data["Partition_key"], "Data": json.dumps(row)} for row in source_reader], config_data["chunk_size"])
    
    size=config_data["chunk_size"]
    start=0

    for chunk in records:
        start+=size
        kinesis.put_object(data=chunk)
        time.sleep(config_data["sleep_time"])

if __name__=="__main__":
    main()
    