#!/usr/bin/env python3

print("🐍 Testing Python setup...")

# Test imports
try:
    import sys
    print(f"✅ Python version: {sys.version}")
    
    # Test our config
    from shared.config import config
    print(f"✅ Config loaded: DB2_HOST = {config.DB2_HOST}")
    
    print("🎉 Basic setup works!")
    
except Exception as e:
    print(f"❌ Error: {e}")