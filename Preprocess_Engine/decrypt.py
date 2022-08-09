# from Key_generator.secret_key import get_secret
# from Key_generator.key_gen import load_key
# from custom_udf import decrypt_val
# from pyspark.sql.functions import udf, lit
# from pyspark.sql.types import StringType
# from pyspark.sql.session import SparkSession
# import datetime
# import json
# import constant


# def decrypt(dir_name , output_folder, config):
#     """

#     :param dir_name:
#     :param output_folder:
#     :param config:
#     """
#     time_stamp = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
#     app_name = dir_name + "_" + time_stamp
#     spark = SparkSession \
#         .builder \
#         .appName(app_name) \
#         .getOrCreate()
   


#     # Register UDF's
#     decrypt = udf(decrypt_val, StringType())

#     # Fetch key from secret manager
#     get_secret()
#     encryptionKey = load_key()

#     with open(constant.DECRYPT_CONFIG,'r') as f:
#         config = json.load(f)

#     # Decrypt the data
#     encrypted = spark.read.format(config["format"]).option("header", config["header"]).load(dir_name)
#     decrypted = encrypted.withColumn(config["column_name"], decrypt(config["column_name"], lit(encryptionKey)))
#     decrypted.write.format(config["format"]).mode(config["mode"]).save(output_folder, header=config["header"])

