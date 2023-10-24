from sodapy import Socrata

class SocrataClient:
    def __init__(self, domain: str, app_token: str):
        self.domain = domain
        self.app_token = app_token
        self.client = self.setup_connection()

    def setup_connection(self):
        print('Setup API connection...')
        print("")
        try:
            client = Socrata(self.domain, self.app_token)
            return client
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def fetch_dataset(self, dataset_id: str, **kwargs):
        if not self.client:
            print("API client is not initialized. Unable to fetch dataset.")
            return None
        
        try:
            results = self.client.get(dataset_id, **kwargs)
            return results
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
