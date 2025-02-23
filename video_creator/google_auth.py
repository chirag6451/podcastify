from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

class GoogleAuth:
    def __init__(self, credentials_path='credentials.json', token_path='token.pickle'):
        """
        Initialize Google authentication handler
        
        Args:
            credentials_path (str): Path to credentials.json file
            token_path (str): Path to save/load token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        # If modifying these scopes, delete the token file
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.metadata'
        ]

    def authenticate(self):
        """
        Authenticate with Google using OAuth 2.0
        
        Returns:
            google.oauth2.credentials.Credentials: The obtained credentials
        """
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        return self.creds

def get_credentials():
    """
    Helper function to quickly get Google credentials
    
    Returns:
        google.oauth2.credentials.Credentials: The obtained credentials
    """
    auth = GoogleAuth()
    return auth.authenticate()

if __name__ == "__main__":
    # Test the authentication
    try:
        creds = get_credentials()
        print("Authentication successful!")
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
