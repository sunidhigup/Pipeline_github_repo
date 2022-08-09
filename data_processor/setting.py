class Settings:
    AWS_CREDENTIALS = {
        "access_key_id": "",
        "secret_access_key": "",
        "region": "us-east-1",
    }

    ORACLE_DB = {

    }

    POSTGRES_DB = {
        "user_name": "postgres",
        "password": "postgres",
        "url": "jdbc:postgresql://localhost:5432/postgres",
        "driver": "org.postgresql.Driver"
    }

    JDBC_jar_path = "/mnt/d/ubuntu/jars/*"
