import getpass
import json
from typing import Union
import urllib.parse

import httplib2

from esap import env
from esap import errors
from esap import storage

ENDPOINT_BASE = 'https://api.esa.io/'
OOB_CALLBACK_URN = 'urn:ietf:wg:oauth:2.0:oob'


def _secure_storage_factory():
  secure_storage = storage.LocalFileStorage('~/.esap/auth', secure=True)
  return secure_storage


class EsaClient(object):

  def __init__(self):
    self.secure_storage = _secure_storage_factory()
    self.client_id = env.Environment.client_id
    self.client_secret = self.secure_storage.get('client_secret')
    if not self._validate_access_token():
      authorization_code = self._authorize()
      access_token = self._fetch_access_token(authorization_code)
      self.secure_storage.set('access_token', access_token)

  def _build_uri(self, endpoint: str, query_params: Union[dict, None] = None):
    uri = ENDPOINT_BASE + endpoint
    if query_params:
      uri += '?' + urllib.parse.urlencode(query_params)
    return uri

  def _build_authorize_uri(self):
    params = {
        'client_id': self.client_id,
        'redirect_uri': OOB_CALLBACK_URN,
        'response_type': 'code',
        'scope': 'read write',
    }
    uri = self._build_uri('oauth/authorize', params)
    return uri

  def _authorize(self):
    authorize_uri = self._build_authorize_uri()
    print('Please open the following URL in your browser:')
    print()
    print(f'    {authorize_uri}')
    print()
    authorization_code = getpass.getpass('Enter the code: ').strip()
    return authorization_code

  def _fetch_access_token(self, authorization_code: str):
    params = {
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': OOB_CALLBACK_URN,
    }
    response = self.post_request('oauth/token', body=params)
    return response['access_token']

  def _validate_access_token(self):
    try:
      self.get_request('oauth/token/info')
      return True
    except errors.HttpError:
      return False

  def get_request(self, endpoint: str, query_params=None, headers=None):
    return self._send_request(endpoint,
                              'GET',
                              query_params=query_params,
                              headers=headers)

  def post_request(self, endpoint: str, body=None, headers=None):
    return self._send_request(endpoint, 'POST', body=body, headers=headers)

  def _send_request(self,
                    endpoint: str,
                    method: str,
                    query_params=None,
                    body=None,
                    headers=None):
    uri = self._build_uri(endpoint, query_params)

    if body is not None:
      body = json.dumps(body)

    if headers is None:
      headers = {}
    headers.update({'Content-Type': 'application/json'})
    access_token = self.secure_storage.get('access_token')
    if access_token:
      headers.update({'Authorization': f'Bearer {access_token}'})

    http = httplib2.Http()
    response, content = http.request(
        uri,
        method,
        body=body,
        headers=headers,
    )

    if response.status < 300:
      if response.status == 204:
        return {}
      return json.loads(content.decode('utf-8'))
    else:
      raise errors.HttpError(response, content, uri=uri)
