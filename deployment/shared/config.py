import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory (deployment folder)
project_root = Path(__file__).parent.parent
env_file = project_root / '.env'

# Load environment variables from .env file
load_dotenv(dotenv_path=env_file)

# Debug: Print if .env file was found
if env_file.exists():
    print(f"📄 Loading .env from: {env_file}")
else:
    print(f"⚠️  .env file not found at: {env_file}")

class Config:
    # Database - Using your actual .env variable names
    DB2_HOST = os.getenv("DB_HOST")
    DB2_PORT = int(os.getenv("DB_PORT", "50000"))
    DB2_DATABASE = os.getenv("DB_NAME")
    DB2_USERNAME = os.getenv("DB_USER")
    DB2_PASSWORD = os.getenv("DB_PASSWORD")
    DB2_PROTOCOL = os.getenv("DB_PROTOCOL", "TCPIP")
    
    # Watson/AI
    WATSONX_PROJECT = os.getenv("WATSONX_PROJECT")
    WATSONX_APIKEY = os.getenv("WATSONX_APIKEY")
    
    # Granite Model
    GRANITE_MODEL_PATH = os.getenv("GRANITE_MODEL_PATH", "./models/granite-embedding-30m-english-Q6_K.gguf")
    
    # API
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_db2_connection_string(cls) -> str:
        # Build connection string from your variables
        connection_parts = [
            f"DATABASE={cls.DB2_DATABASE}",
            f"HOSTNAME={cls.DB2_HOST}",
            f"PORT={cls.DB2_PORT}",
            f"PROTOCOL={cls.DB2_PROTOCOL}",
            f"UID={cls.DB2_USERNAME}",
            f"PWD={cls.DB2_PASSWORD}"
        ]
        
        # Add SSL if needed (common for IBM Cloud DB2)
        if str(cls.DB2_PORT) == "50001":
            connection_parts.append("SECURITY=SSL")
        
        return ";".join(connection_parts) + ";"
    
    def validate_config(self):
        """Validate that required DB2 config is present"""
        required_vars = {
            'DB_HOST': self.DB2_HOST,
            'DB_NAME': self.DB2_DATABASE,
            'DB_USER': self.DB2_USERNAME,
            'DB_PASSWORD': self.DB2_PASSWORD
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            print("Please update your .env file with these values")
            return False
        
        print(f"✅ All required DB2 config variables are set")
        return True

config = Config()

# Debug: Show what was actually loaded (mask password)
print(f"🔧 Config loaded:")
print(f"   DB_HOST: {config.DB2_HOST}")
print(f"   DB_PORT: {config.DB2_PORT}")
print(f"   DB_NAME: {config.DB2_DATABASE}")
print(f"   DB_USER: {config.DB2_USERNAME}")
print(f"   DB_PASSWORD: {'***' if config.DB2_PASSWORD else 'NOT SET'}")