from pyspark.sql.types import StructType,StructField, StringType, IntegerType, TimestampType, DateType, DoubleType

class DataType:
    """[summary]
    """    

    def toDataType(typ):
        """[summary]

        Args:
            typ ([type]): [description]

        Returns:
            [type]: [description]
        """        

        #Converting from string to given type
        if(typ == "int"): return IntegerType()

        if(typ == "string"): return StringType()

        if(typ == "date"): return DateType()

        if(typ == "double"): return DoubleType()

        if(typ == "timestamp"): return TimestampType()
    
    