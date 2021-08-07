import click
from commands.auth import get_token
import http.client
import urllib
import sys
import json

HOST = 'api.clickup.com'
BASE_PATH = '/api/v2/'


def make_api_request(path):
    connection = http.client.HTTPSConnection(HOST)
    headers = {'Authorization': get_token()}
    url = urllib.parse.urljoin(BASE_PATH, path)
    if sys.stdout.isatty():
        click.echo(click.style(url, fg='blue'))
    connection.request('GET', url, headers=headers)
    response = connection.getresponse()
    response_body = response.read().decode()
    response_json = json.loads(response_body)
    return response_json
