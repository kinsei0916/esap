import json
from typing import Union
import urllib.parse

import httplib2

from esap import auth
from esap import errors

ENDPOINT_BASE = 'https://api.esa.io/'


class EsaClient(object):

  def __init__(self):
    self.auth = auth.Auth()
    self.auth.authorize()

  def _build_uri(self, endpoint: str, query_params: Union[dict, None] = None):
    uri = ENDPOINT_BASE + endpoint
    if query_params:
      uri += '?' + urllib.parse.urlencode(query_params)
    return uri

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

    uri, headers, body = self.auth.add_token(uri,
                                             method=method,
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
