from datetime import date

import configparser
import json
import os
import requests

class ClientQuotes:
    headers = None

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        assert 'RAPIDAPI_SKYSCANNER_KEY' in config['DEFAULT'], 'Could not find key \'RAPIDAPI_SKYSCANNER_KEY\' in config.ini. Exit.'
        assert 'RAPIDAPI_SKYSCANNER_HOST' in config['DEFAULT'], 'Could not find key \'RAPIDAPI_SKYSCANNER_HOST\' in config.ini. Exit.'
        rapidapi_skyscanner_key = config['DEFAULT']['RAPIDAPI_SKYSCANNER_KEY']
        rapidapi_skyscanner_host = config['DEFAULT']['RAPIDAPI_SKYSCANNER_HOST']

        self.headers = {
            'x-rapidapi-key': rapidapi_skyscanner_key,
            'x-rapidapi-host': rapidapi_skyscanner_host
        }

    def get_city_id(self, place_name: str):
        result = None

        # Query the Skyscanner API
        url = 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/autosuggest/v1.0/US/USD/en-US/'
        params = {'query': place_name}
        response = requests.request('GET', url, headers=self.headers, params=params)
        assert response.status_code == 200, 'Response code = {} != 200. Exit.'.format(response.status_code)
        
        # Parse JSON response
        parsed = json.loads(response.text)
        result = json.dumps(parsed, indent=3, sort_keys=True)
        #print(result) # Debugging
        places = parsed['Places']
        found = False
        for i in range(len(places)):
            place = places[i]
            if place['PlaceName'] == place_name:
                result = place['CityId']
                found = True
                break
        
        return found, result
    
    def get_quote(self, origin: str, destination: str, outbound_date: date):
        result = None

        # Query the Skyscanner API
        url = 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/{}/{}/{}'.format(origin, destination, outbound_date)
        params = {'inboundpartialdate': ''}
        response = requests.request('GET', url, headers=self.headers, params=params)
        assert response.status_code in [200, 429], 'Response code = {} not in [200, 429]. Exit.'.format(response.status_code)

        if response.status_code == 200:
            # Parse JSON response
            parsed = json.loads(response.text)
            #print(json.dumps(parsed, indent=3, sort_keys=True)) # Debugging
            quotes = parsed['Quotes']
            if len(quotes) > 0:
                result = min([quote['MinPrice'] for quote in quotes])

        return response.status_code, result