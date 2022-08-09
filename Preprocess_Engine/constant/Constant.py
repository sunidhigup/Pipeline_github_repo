 
DICT = {
            "client_name": "" ,
            "timestamp": "",
            "filename": ""
    }
    
STATUS_TABLE_NAME = "dep_preprocessor_file_classification_status"
FILE_TABLE = "dep_preprocessor_file_classification"


AWS_CREDENTIALS = {
        "format": "kinesis",
        "region": "us-east-1",
        "endpointUrl": "kinesis.us-east-1.amazonaws.com",
        "startingposition": "latest"
    }

DECRYPT_CONFIG = "config/preprocessor_config.json",
CONFIG_PATH = "config/path.json"

class commmon_constants:
    STATUS_COMPLETED = "Completed"
    STATUS = "Status"
    ID = "id"
    
class profile_env_params:
    BUCKETNAME="depconfig"
    KEYNAME="Preprocess_Engine/Config/path.json"

class extract_constants:
    OPT = "unzipped"
    OPT_PERF = "Operation performed"
    PROCESS_PATH = "Processed_path"
    EXT_PREFIX = "extracted_prefix"
    RULE_ENGINE = "Rule_engine"
    INPUT = "Input"
    SLASH = "/"

class preprocessor_constants:
    INFO = "Info"
    INFO_START = "[******* Starting Preprocessing *********]"
    DEST_BUCKET = "destination_bucket"
    _DEST_KEY = "destination_key"
    SLASH = "/"
    TIMESTAMP = "timestamp"
    EXT = "extension"
    ZIP = "zip"
    INFO_ZIP = "[******* Found zip file, trying to unzip *********]"
    INFO_EXT = "[******* Extraction successful *********]"
    INFO_ERROR = "[******* Error during extraction..trying to decrypt*********]"
    TXT = "txt"
    INFO_FILE_FOUND_TXT = "[******* Found text file, renaming it accordingly *********]"
    OPT_PER = "Operation performed"
    RENAME = "Renamed"
    ID = "id"
    TIMESTAMP = "timestamp"
    FILENAME = "filename"
    INFO_RENAME_TXT = "[******* Renaming successful of text file *********]"
    INFO_FILE_FOUND_CSV = "[******* Found csv file, renaming it accordingly *********]"
    INFO_RENAME_CSV = "[******* Renaming successful of csv file *********]"
    STATE_FILE = "file_state"
    STATE_PROCESSED = "Processed"
    CSV = "csv"
    STATE_SKIP = "Skip_preprocessing"
    ITEMS = "Items"

