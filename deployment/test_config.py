#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.config import config

def test_config_loading():
    """Test that configuration is loaded correctly from .env"""
    try:
        print("🔍 Testing configuration loading...")
        print(f"Current working directory: {os.getcwd()}")
        
        # Check if .env file exists
        env_file_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_file_path):
            print(f"✅ Found .env file at: {env_file_path}")
        else:
            print(f"⚠️  .env file not found at: {env_file_path}")
        
        print("\n📋 Configuration values:")
        print(f"DB_HOST: {config.DB2_HOST}")
        print(f"DB_PORT: {config.DB2_PORT}")
        print(f"DB_NAME: {config.DB2_DATABASE}")
        print(f"DB_USER: {config.DB2_USERNAME}")
        print(f"DB_PASSWORD: {'*' * len(config.DB2_PASSWORD) if config.DB2_PASSWORD else 'Not set'}")
        print(f"WATSONX_PROJECT: {config.WATSONX_PROJECT}")
        print(f"GRANITE_MODEL_PATH: {config.GRANITE_MODEL_PATH}")
        print(f"LOG_LEVEL: {config.LOG_LEVEL}")
        
        print(f"\n🔗 Generated connection string:")
        connection_string = config.get_db2_connection_string()
        # Mask password in output
        masked_connection = connection_string.replace(f"PWD={config.DB2_PASSWORD}", "PWD=***")
        print(f"{masked_connection}")
        
        # Validate configuration
        print(f"\n🔍 Validating configuration...")
        if config.validate_config():
            print(f"✅ Configuration is valid and ready for DB2 connection!")
        else:
            print(f"❌ Configuration validation failed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    test_config_loading()