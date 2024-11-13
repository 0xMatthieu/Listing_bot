import requests
from dotenv import load_dotenv
import os
import json

class WebhookAlerts:
    def __init__(self, token_id):
        self.token_id = token_id #os.environ.get('token_id')
        self.url = f'https://webhook.site/token/{token_id}/requests'
        self.data_path = './data'
        self.last_request_file = os.path.join(self.data_path, 'last_request.json')
        os.makedirs(self.data_path, exist_ok=True)
        self.last_request_id = self.get_last_request_id()
        if self.last_request_id is None:
            self.save_last_request(self.fetch_request())
            self.last_request_id = self.get_last_request_id()

    def fetch_request(self):
        """Fetches the latest request from Webhook.site."""
        response = requests.get(self.url)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                return data['data'][0]  # Return the latest request data
        return None

    def save_last_request(self, request_data):
        """Saves the last request data to a JSON file."""
        with open(self.last_request_file, 'w') as file:
            json.dump(request_data, file)

    def get_last_request_id(self):
        """Reads the last saved request ID from the JSON file."""
        if os.path.exists(self.last_request_file):
            with open(self.last_request_file, 'r') as file:
                last_request = json.load(file)
                if last_request:
                    return last_request.get('uuid')
        return None

    def get_new_request_content(self):
        """Fetches new request content if a new ID is received, and updates the JSON file."""
        latest_request = self.fetch_request()
        if latest_request:
            if latest_request['uuid'] != self.last_request_id:
                # Save the new request as the last request
                self.save_last_request(latest_request)
                self.last_request_id = latest_request['uuid']
                # Return the content of the new request
                return latest_request['content']
        return None
    
    def get_currency_if_new_coin(self):
        """Checks if the latest request is of type 'new_coin' and retrieves the currency."""
        content = self.get_new_request_content()
        if content:
            try:
                data = json.loads(content)
                if data.get('type') == 'new_coin':
                    return data.get('currency')
            except json.JSONDecodeError:
                print("Error decoding JSON content.")
        return None
    
    

# Usage example:
# webhook = WebhookAlerts(os.environ.get('token_id'))
# new_content = webhook.get_new_request_content()
# if new_content:
#     print("New content received:", new_content)
# new_currency = webhook.get_currency_if_new_coin()
# if new_currency:
#     print("New coin listed:", new_currency)
