import dataclasses
import getpass
from typing import Literal, Union

import httplib2

from esap import errors
from esap import oauth2
from esap import storage

ENDPOINT_BASE = 'https://api.esa.io/'
OOB_CALLBACK_URN = 'urn:ietf:wg:oauth:2.0:oob'


@dataclasses.dataclass
class ClientSecrets:
  client_id: str
  client_secret: str


@dataclasses.dataclass
class Credentials:
  access_token: Union[str, None] = None
  refresh_token: Union[str, None] = None
  token_type: Union[str, None] = 'Bearer'
  expires_at: Union[str, None] = None


@dataclasses.dataclass
class AuthOptions:
  client_secrets_backend: Literal['file', 'in_memory'] = 'file'
  client_secrets_file: str = '~/.esap/client_secrets'
  client_secrets: Union[ClientSecrets, None] = None
  credentials_backend: Literal['file', 'in_memory'] = 'file'
  credentials_file: str = '~/.esap/credentials'
  credentials: Union[Credentials, None] = None

  def __post_init__(self):
    if self.client_secrets_backend == 'file':
      if self.client_secrets_file is None:
        raise ValueError('`client_secrets_file` must be specified')
    elif self.client_secrets_backend == 'in_memory':
      if self.client_secrets is None:
        raise ValueError('`client_secrets` must be specified')
    else:
      raise ValueError('client_secrets_backend must be `file` or `in_memory`')

    if self.credentials_backend == 'file':
      if self.credentials_file is None:
        raise ValueError('`credentials_file` must be specified')
    elif self.credentials_backend == 'in_memory':
      if self.credentials is None:
        self.credentials = Credentials()
    else:
      raise ValueError('credentials_backend must be `file` or `in_memory`')


def _load_client_secrets_storage(options: AuthOptions):
  if options.client_secrets_backend == 'file':
    return storage.LocalFileStorage(options.client_secrets_file, secure=True)
  elif options.client_secrets_backend == 'in_memory':
    return storage.InMemoryStorage(dataclasses.asdict(options.client_secrets))
  else:
    raise ValueError('client_secrets_backend must be `file` or `in_memory`')


def _load_credentials_storage(options: AuthOptions):
  if options.credentials_backend == 'file':
    return storage.LocalFileStorage(options.credentials_file, secure=True)
  elif options.credentials_backend == 'in_memory':
    return storage.InMemoryStorage(dataclasses.asdict(options.credentials))
  else:
    raise ValueError('credentials_backend must be `file` or `in_memory`')


class Auth(object):

  def __init__(self, options: Union[AuthOptions, None] = None):
    if options is None:
      options = AuthOptions()
    client_secrets = _load_client_secrets_storage(options)
    credentials = _load_credentials_storage(options)
    self.client = oauth2.OAuth2Client(client_secrets,
                                      credentials,
                                      scope=['read', 'write'])

  def authorize(self):
    if self.client.access_token is None:
      self._get_authorization_code()
      self._fetch_access_token()
      print('Authorization succeeded!')

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
