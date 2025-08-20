#!/usr/bin/env python3
"""
Prepare Token for GitHub Secrets
This script converts token.pickle to base64 format for GitHub secrets.
"""

import base64
import os

def prepare_token_for_github():
    """Convert token.pickle to base64 for GitHub secrets"""
    
    print("🔐 Preparing token.pickle for GitHub secrets...")
    
    # Check if token.pickle exists
    if not os.path.exists('token.pickle'):
        print("❌ token.pickle not found!")
        print("Please run generate_token.py first to create the token.")
        return False
    
    try:
        # Read the token.pickle file
        with open('token.pickle', 'rb') as token_file:
            token_data = token_file.read()
        
        # Convert to base64
        token_base64 = base64.b64encode(token_data).decode('utf-8')
        
        # Save to a text file for easy copying
        with open('token_for_github.txt', 'w') as output_file:
            output_file.write(token_base64)
        
        print("✅ Successfully converted token.pickle to base64!")
        print(f"📄 Token saved to: token_for_github.txt")
        print(f"📏 Token size: {len(token_data)} bytes")
        print(f"🔢 Base64 length: {len(token_base64)} characters")
        
        print("\n📋 Next steps:")
        print("1. Copy the content of token_for_github.txt")
        print("2. Go to GitHub repository → Settings → Secrets → Actions")
        print("3. Create/update GOOGLE_TOKEN secret with the copied content")
        print("4. Delete both token.pickle and token_for_github.txt for security")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to prepare token: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SubsplashCalendarBridge - Token Preparation for GitHub")
    print("=" * 60)
    
    success = prepare_token_for_github()
    
    if success:
        print("\n🎉 Token preparation completed successfully!")
    else:
        print("\n💥 Token preparation failed. Please check the error above.")
