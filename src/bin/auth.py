import sys
import os

# Add parent directory to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from authentication import get_authorization_url, exchange_code_for_tokens
    from helpers.env_loader import load_env_file
except ImportError as e:
    print(f"Error: Could not import necessary modules: {e}")
    sys.exit(1)

def main():
    load_env_file()
    
    print("=== Google Tag Manager API OAuth 2.0 Setup ===")
    
    # Defaults from environment
    env_client_id = os.getenv("GTM_CLIENT_ID")
    env_client_secret = os.getenv("GTM_CLIENT_SECRET")
    
    client_id = input(f"Enter your Client ID [{env_client_id or 'none'}]: ").strip() or env_client_id
    client_secret = input(f"Enter your Client Secret [{env_client_secret or 'none'}]: ").strip() or env_client_secret
    
    if not client_id or not client_secret:
        print("Error: Client ID and Client Secret are required.")
        return

    redirect_uri = "http://localhost:8000"# "urn:ietf:wg:oauth:2.0:oob"
    
    try:
        auth_url = get_authorization_url(client_id=client_id, redirect_uri=redirect_uri)
    except Exception as e:
        print(f"Error generating authorization URL: {e}")
        return
    
    print("\n1. Go to the following URL in your browser:")
    print(auth_url)
    
    print("\n2. Authorize the application and copy the 'authorization code'.")
    code = input("3. Enter the authorization code here: ").strip()
    
    try:
        tokens = exchange_code_for_tokens(code=code, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
        
        print("\n=== SUCCESS ===")
        print(f"Access Token: {tokens.get('access_token')}")
        print(f"Refresh Token: {tokens.get('refresh_token')}")
        print("\nAdd these to your .env file:")
        print(f"GTM_CLIENT_ID={client_id}")
        print(f"GTM_CLIENT_SECRET={client_secret}")
        print(f"GTM_REFRESH_TOKEN={tokens.get('refresh_token')}")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
