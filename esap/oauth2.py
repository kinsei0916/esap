import oauthlib.oauth2

from esap import storage


class OAuth2Client(oauthlib.oauth2.WebApplicationClient):
  """A client utilizing the authorization code grant workflow."""

  def __init__(self, client_id: str, client_secret: str,
               credential_storage: storage.BaseStorage, **kwargs):
    super().__init__(client_id, **kwargs)
    self.client_secret = client_secret
    self.storage = credential_storage
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
    credentials = self.storage.to_dict()
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
    self.storage.set_from_dict(credentials)
