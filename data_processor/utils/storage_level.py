import pyspark


class StorageLevel:

    def getStorageLevel(self, persist_type):
        """

        :param persist_type:
        :return:
        """
        storage_level = {
            "DISK_ONLY": pyspark.StorageLevel.DISK_ONLY,
            "DISK_ONLY_2": pyspark.StorageLevel.DISK_ONLY_2,
            "MEMORY_ONLY": pyspark.StorageLevel.MEMORY_ONLY,
            "MEMORY_ONLY_2": pyspark.StorageLevel.MEMORY_ONLY_2,
            "MEMORY_AND_DISK": pyspark.StorageLevel.MEMORY_AND_DISK,
            "MEMORY_AND_DISK_2": pyspark.StorageLevel.MEMORY_AND_DISK_2
        }

        return storage_level.get(persist_type, pyspark.StorageLevel.MEMORY_AND_DISK)
