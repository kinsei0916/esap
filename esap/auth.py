import getpass
from typing import Union

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


class Auth(object):

  def __init__(self):
    self.client = oauth2.OAuth2Client(_client_secrets_storage_factory(),
                                      _credentials_storage_factory(),
                                      scope=['read', 'write'])

  def authorize(self):
    if self.client.access_token is None:
      self._get_authorization_code()
      self._fetch_access_token()

  def add_token(
      self,
      uri: str,
      method: str,
      body: Union[str, None] = None,
      headers: Union[dict[str, str], None] = None
  ) -> tuple[str, dict[str, str], Union[str, None]]:
    return self.client.add_token(uri,
                                 http_method=method,
                                 body=body,
                                 headers=headers)

  def _build_uri(self, endpoint: str):
    return ENDPOINT_BASE + endpoint

  def _get_authorization_code(self):
    uri, _, _ = self.client.prepare_authorization_request(
        self._build_uri('oauth/authorize'), redirect_url=OOB_CALLBACK_URN)
    print('Please open the following URL in your browser:')
    print()
    print(f'    {uri}')
    print()
    code = getpass.getpass('Enter the code: ').strip()
    self.client.set_code(code)

  def _send_auth_request(self, uri: str, headers=None, body=None):
    http = httplib2.Http()
    response, content = http.request(uri, 'POST', body=body, headers=headers)
    if response.status != 200:
      raise errors.HttpError(response, content, uri=uri)
    return content

  def _fetch_access_token(self):
    uri, headers, body = self.client.prepare_token_request(
        self._build_uri('oauth/token'))
    resp_content = self._send_auth_request(uri, headers, body)
    self.client.parse_request_body_response(resp_content)
