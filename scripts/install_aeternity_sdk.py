#!/usr/bin/env python3
"""Script to install the æternity SDK and test real tokenization."""

import subprocess
import sys
import os

def install_aeternity_sdk():
    """Install the æternity SDK from GitHub."""
    print("🔧 Installing æternity SDK from GitHub...")
    
    try:
        # Install from GitHub
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "git+https://github.com/aeternity/aepp-sdk-python.git"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ æternity SDK installed successfully!")
            return True
        else:
            print(f"❌ Failed to install æternity SDK: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing æternity SDK: {e}")
        return False

def test_aeternity_import():
    """Test if æternity SDK can be imported."""
    print("🧪 Testing æternity SDK import...")
    
    try:
        import aeternity
        print("✅ æternity SDK imported successfully!")
        print(f"   Version: {aeternity.__version__ if hasattr(aeternity, '__version__') else 'Unknown'}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import æternity SDK: {e}")
        print("   Note: The package might be installed as 'aepp-sdk'")
        try:
            import aepp_sdk
            print("✅ Found aepp-sdk package instead!")
            return True
        except ImportError:
            return False

def main():
    """Main installation and test function."""
    print("🚀 æternity SDK Installation and Test Script")
    print("=" * 50)
    
    # Install SDK
    if not install_aeternity_sdk():
        print("❌ Installation failed. Exiting.")
        return False
    
    # Test import
    if not test_aeternity_import():
        print("❌ Import test failed. Exiting.")
        return False
    
    print("\n🎉 æternity SDK is ready to use!")
    print("\nNext steps:")
    print("1. Set your æternity private key in .env file:")
    print("   AETERNITY_PRIVATE_KEY=your_private_key_here")
    print("2. Update the tokenization service to use real blockchain")
    print("3. Deploy contracts to æternity testnet")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
