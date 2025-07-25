import os

class Config:
    # Database
    DB2_HOST = os.getenv("DB2_HOST", "localhost")
    DB2_PORT = int(os.getenv("DB2_PORT", "50000"))
    DB2_DATABASE = os.getenv("DB2_DATABASE", "vectordb")
    DB2_USERNAME = os.getenv("DB2_USERNAME", "db2inst1")
    DB2_PASSWORD = os.getenv("DB2_PASSWORD", "password")
    DB2_CONNECTION_STRING = os.getenv("DB2_CONNECTION_STRING", "")
    
    # Granite Model (matching your notebook)
    GRANITE_MODEL_PATH = os.getenv("GRANITE_MODEL_PATH", "./models/granite-embedding-30m-english-Q6_K.gguf")
    
    # API
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_db2_connection_string(cls) -> str:
        if cls.DB2_CONNECTION_STRING:
            return cls.DB2_CONNECTION_STRING
        return f"DATABASE={cls.DB2_DATABASE};HOSTNAME={cls.DB2_HOST};PORT={cls.DB2_PORT};UID={cls.DB2_USERNAME};PWD={cls.DB2_PASSWORD};"

config = Config()