import click
import http.client
import urllib
import sys
import json
from commands.config import direct_get

HOST = 'api.clickup.com'
BASE_PATH = '/api/v2/'


def make_api_request(path):
    connection = http.client.HTTPSConnection(HOST)
    headers = {'Authorization': direct_get('api-key')}
    url = urllib.parse.urljoin(BASE_PATH, path)
    if sys.stdout.isatty():
        click.echo(click.style(url, fg='blue'))
    connection.request('GET', url, headers=headers)
    response = connection.getresponse()
    response_body = response.read().decode()
    response_json = json.loads(response_body)
    return response_json
