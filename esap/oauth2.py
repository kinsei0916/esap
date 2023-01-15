import oauthlib.oauth2

from esap import errors
from esap import storage


def _load_client_secrets(client_secrets_storage: storage.BaseStorage):
  client_id = client_secrets_storage.get('client_id')
  if client_id is None:
    raise errors.AuthenticationError('`client_id` is not found.')
  client_secret = client_secrets_storage.get('client_secret')
  if client_secret is None:
    raise errors.AuthenticationError('`client_secret` is not found.')
  return client_id, client_secret


class OAuth2Client(oauthlib.oauth2.WebApplicationClient):
  """A client utilizing the authorization code grant workflow."""

  def __init__(self, client_secrets_storage: storage.BaseStorage,
               credential_storage: storage.BaseStorage, **kwargs):
    client_id, client_secret = _load_client_secrets(client_secrets_storage)
    super().__init__(client_id, **kwargs)
    self.client_secret = client_secret
    self.credential_storage = credential_storage
    self._load_credentials()

  def set_code(self, code: str):
    self.code = code

  def prepare_token_request(self, *args, **kwargs):
    kwargs['client_secret'] = self.client_secret
    return super().prepare_token_request(*args, **kwargs)

  def parse_request_body_response(self, *args, **kwargs):
    super().parse_request_body_response(*args, **kwargs)
    self._save_credentials()

  def _load_credentials(self):
    credentials = self.credential_storage.to_dict()
    self.access_token = credentials.get('access_token')
    self.refresh_token = credentials.get('refresh_token')
    self.token_type = credentials.get('token_type', 'Bearer')
    self._expires_at = credentials.get('expires_at')

  def _save_credentials(self):
    credentials = {
        'access_token': self.access_token or self.token.get('access_token'),
        'refresh_token': self.refresh_token or self.token.get('refresh_token'),
        'token_type': self.token_type or self.token.get('token_type'),
        'expires_at':
            self._expires_at  # type: ignore
    }
    credentials = {k: v for k, v in credentials.items() if v is not None}
    self.credential_storage.set_from_dict(credentials)
