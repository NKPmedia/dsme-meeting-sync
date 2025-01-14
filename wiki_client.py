import os

import requests
from bs4 import BeautifulSoup


class MediaWikiClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        # Step 1: Get login token
        params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json'
        }
        response = self.session.get(url=self.base_url + '/api.php', params=params)
        response.raise_for_status()

        login_token = response.json()['query']['tokens']['logintoken']

        # Step 2: Log in with the token and credentials
        data = {
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password,
            'lgtoken': login_token,
            'format': 'json'
        }

        response = self.session.post(url=self.base_url + '/api.php', data=data)
        response.raise_for_status()

        if response.json()['login']['result'] != "Success":
            raise Exception("Login failed!")

    def fetch_page_html(self, page_title):
        # Fetch the page content as HTML
        params = {
            'action': 'parse',
            'page': page_title,
            'format': 'json'
        }

        response = self.session.get(url=self.base_url + '/api.php', params=params)
        response.raise_for_status()

        html_content = response.json()['parse']['text']['*']

        return html_content