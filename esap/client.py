import getpass
import json
from typing import Union
import urllib.parse

import httplib2

from esap import errors
from esap import oauth2
from esap import storage

ENDPOINT_BASE = 'https://api.esa.io/'
OOB_CALLBACK_URN = 'urn:ietf:wg:oauth:2.0:oob'


def _client_secrets_storage_factory():
  return storage.LocalFileStorage('~/.esap/client_secrets', secure=True)


def _credentials_storage_factory():
  return storage.LocalFileStorage('~/.esap/credentials', secure=True)


class EsaClient(object):

  def __init__(self):
    self.oauth_client = oauth2.OAuth2Client(_client_secrets_storage_factory(),
                                            _credentials_storage_factory(),
                                            scope=['read', 'write'])
    if not self._validate_access_token():
      self._authorize()
      self._fetch_access_token()

  def _build_uri(self, endpoint: str, query_params: Union[dict, None] = None):
    uri = ENDPOINT_BASE + endpoint
    if query_params:
      uri += '?' + urllib.parse.urlencode(query_params)
    return uri

  def _build_authorize_uri(self):
    uri, _, _ = self.oauth_client.prepare_authorization_request(
        self._build_uri('oauth/authorize'), redirect_url=OOB_CALLBACK_URN)
    return uri

  def _authorize(self):
    authorize_uri = self._build_authorize_uri()
    print('Please open the following URL in your browser:')
    print()
    print(f'    {authorize_uri}')
    print()
    code = getpass.getpass('Enter the code: ').strip()
    self.oauth_client.set_code(code)

  def _send_auth_request(self, uri: str, headers=None, body=None):
    http = httplib2.Http()
    response, content = http.request(uri, 'POST', body=body, headers=headers)
    if response.status >= 300:
      raise errors.HttpError(response, content, uri=uri)
    return content

  def _fetch_access_token(self):
    uri, headers, body = self.oauth_client.prepare_token_request(
        self._build_uri('oauth/token'))
    resp_content = self._send_auth_request(uri, headers, body)
    self.oauth_client.parse_request_body_response(resp_content)

  def _validate_access_token(self):
    if self.oauth_client.access_token is None:
      return False
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

    uri, headers, body = self.oauth_client.add_token(uri,
                                                     http_method=method,
                                                     body=body,
                                                     headers=headers)

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
