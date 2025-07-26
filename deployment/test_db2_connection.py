#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ibm_db
from shared.config import config

def test_db2_connection():
    """Test direct DB2 connection"""
    try:
        print("🔍 Testing DB2 connection...")
        print(f"Host: {config.DB2_HOST}")
        print(f"Port: {config.DB2_PORT}")
        print(f"Database: {config.DB2_DATABASE}")
        print(f"Username: {config.DB2_USERNAME}")
        
        # Create connection string
        connection_string = config.get_db2_connection_string()
        print(f"Connection string: {connection_string}")
        
        # Attempt connection
        print("\n📡 Connecting to DB2...")
        connection = ibm_db.connect(connection_string, "", "")
        
        if connection:
            print("✅ Successfully connected to IBM DB2!")
            
            # Test a simple query
            print("\n🧪 Testing query execution...")
            stmt = ibm_db.exec_immediate(connection, "SELECT 1 FROM SYSIBM.SYSDUMMY1")
            if stmt:
                result = ibm_db.fetch_tuple(stmt)
                print(f"✅ Query successful: {result}")
            
            # Check if vector tables exist
            print("\n📋 Checking for existing tables...")
            try:
                stmt = ibm_db.exec_immediate(connection, 
                    "SELECT TABNAME FROM SYSCAT.TABLES WHERE TABSCHEMA = CURRENT_SCHEMA AND TABNAME LIKE '%DOCUMENT%'")
                
                tables = []
                while ibm_db.fetch_row(stmt):
                    table_name = ibm_db.result(stmt, 0)
                    tables.append(table_name)
                
                if tables:
                    print(f"📊 Found existing tables: {tables}")
                else:
                    print("📝 No existing document tables found (will be created)")
                    
            except Exception as e:
                print(f"⚠️  Could not check tables: {e}")
            
            # Close connection
            ibm_db.close(connection)
            print("\n🎉 DB2 connection test successful!")
            return True
            
        else:
            print("❌ Failed to connect to DB2")
            return False
            
    except Exception as e:
        print(f"❌ DB2 connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your DB2 hostname and port")
        print("2. Verify your username and password") 
        print("3. Ensure the database name is correct")
        print("4. Check if DB2 server is running and accessible")
        print("5. Verify network connectivity (firewalls, VPN, etc.)")
        return False

if __name__ == "__main__":
    test_db2_connection()