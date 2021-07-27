import requests
import json
import dateutil.parser
from datetime import datetime


# baseUrl = 'https://server-preprod.humm-box.com/'
baseUrl = 'https://server.humm-box.com/'


def get_bearer(file):
    try:
        with open(file) as bearer_file:
            bearer = bearer_file.readline().rstrip("\n")
            bearer_file.close()
            return bearer
    except(FileNotFoundError):
        return None


def get_log(device, bearer):
    url = baseUrl + 'api/devices/' + device + '/logs'
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': bearer,
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        'Origin': 'https://app.humm-box.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://app.humm-box.com/',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        data = response.json()
        for item in data:
            item['timestamp'] = datetime.timestamp(
                dateutil.parser.parse(item['time']))
        return data
    except(requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
        return None


def get_start(log):
    for item in log:
        if item['message'] == 'Device rebooted by pushing External button':
            return item['timestamp']
    return None


def get_config(device, bearer):
    url = baseUrl + 'api/devices/' + device
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': bearer,
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        'Origin': 'https://app.humm-box.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://app.humm-box.com/',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        data = response.json()
        return data
    except(requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
        return None


def get_measure(device, bearer):
    url = baseUrl + 'api/devices/' + device + '/measures'
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': bearer,
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Origin': 'https://app-preprod.humm-box.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://app-preprod.humm-box.com/',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    params = (
        ('skip', '0'),
        ('limit', '200'),
        # ('exports', 'true'),
        ('sort[created_at]', 'desc'),
    )

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return None
        data = response.json()
        for item in data:
            item['timestamp'] = datetime.timestamp(
                dateutil.parser.parse(item['created_at']))
            # + (60 * 60 * 2)
        return data
    except(requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
        return None
    # NB. Original query string below. It seems impossible to parse and
    # reproduce query strings 100% accurately so the one below is given
    # in case the reproduced version is not "correct".
    # response = requests.get(baseUrl + 'api/devices/2004E2/measures?skip=0&limit=200&sort\[created_at\]=desc', headers=headers)


def change_config(device, bearer, new_config):
    url = baseUrl + 'api/devices/' + device
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': bearer,
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://app.humm-box.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://app.humm-box.com/',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    data = json.dumps(new_config)
    try:
        response = requests.patch(url, headers=headers, data=data)
        if response.status_code != 200:
            return False
        return True
    except(requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
        return None
