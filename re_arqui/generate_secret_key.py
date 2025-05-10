"""
Script to generate and store a Django secret key for production use
"""
import json
import os
import secrets

def generate_secret_key():
    """Generate a secure random string for use as a Django secret key"""
    return secrets.token_urlsafe(50)

def main():
    """Main function to generate and save the secret key"""
    # Get the base directory where this script is running
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate a new secret key
    secret_key = generate_secret_key()
    
    # Create a JSON file with the secret key
    with open(os.path.join(base_dir, 'secret_key.json'), 'w') as f:
        json.dump({'SECRET_KEY': secret_key}, f)
    
    print("Secret key generated and stored in secret_key.json")
    print("Keep this file secure and do not commit it to version control!")

if __name__ == "__main__":
    main() 