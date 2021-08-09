import click
import http.client
import urllib
import sys
import json
from typing import Union
from enum import Enum
from commands.config import direct_get

HOST = 'api.clickup.com'
BASE_PATH = '/api/v2/'


class MethodType(Enum):
    GET = 'GET',
    POST = 'POST',
    PUT = 'PUT',
    DELETE = 'DELETE'


def make_api_request(path: str,
                     method: MethodType = 'GET',
                     body: Union[str, dict] = None,
                     verbose: bool = False):
    connection = http.client.HTTPSConnection(HOST)
    headers = {'Authorization': direct_get('api-key')}
    url = urllib.parse.urljoin(BASE_PATH, path)
    if sys.stdout.isatty():
        click.echo(click.style(url, fg='blue'))
    if method != 'GET' and body is not None:
        if type(body) is dict:
            body = json.dumps(body)
        headers['Content-Type'] = 'application/json'
        connection.request(method, url, headers=headers, body=body)
    else:
        connection.request(method, url, headers=headers)
    response = connection.getresponse()
    response_body = response.read().decode()
    if verbose:
        click.echo(response_body)
    response_json = json.loads(response_body)
    if response.code >= 400:
        click.echo(click.style('Error', fg='red') +
                   ': server responded with a %s status code.' % response.code,
                   err=True)
        click.echo(response_json, err=True)
    return response_json
