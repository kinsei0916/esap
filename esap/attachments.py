import json
from typing import Union
import urllib.parse

import httplib2
import pandas as pd

from esap import errors
from esap import resources
from esap import storage
from esap.client import EsaClient
from esap.markdown import embedding
from esap.markdown import table

CACHE_STORAGE = storage.LocalFileStorage('~/.esap/attachments_cache')


def _fetch_attachment_policies(client: EsaClient, team_name: str,
                               file: resources.File):
  params = {
      'type': file.mimetype,
      'name': file.name,
      'size': file.size,
  }
  response = client.post_request(
      f'v1/teams/{team_name}/attachments/policies',
      body=params,
  )
  return response


BOUNDARY = '-------314159265358979323846'
CRLF = b'\r\n'


def _encode_multipart_form_fata(fields: dict[str, Union[str, resources.File]]):
  lines = []
  for key, value in fields.items():
    lines.append(f'--{BOUNDARY}')
    if isinstance(value, resources.File):
      lines.append(f'Content-Disposition: form-data; name="{key}"; '
                   f'filename="{value.name}"')
      lines.append(f'Content-Type: {value.mimetype}')
      lines.append('')
      lines.append(value.read())
    else:
      lines.append(f'Content-Disposition: form-data; name="{key}"')
      lines.append('')
      lines.append(value)
  lines.append('--' + BOUNDARY + '--')
  lines.append('')
  lines = [
      line.encode('utf-8') if isinstance(line, str) else line for line in lines
  ]
  body = CRLF.join(lines)
  content_type = f'multipart/form-data; boundary={BOUNDARY}'
  return content_type, body


def _post_s3_request(endpoint: str, fields: dict[str, Union[str,
                                                            resources.File]]):
  content_type, body = _encode_multipart_form_fata(fields)
  headers = {'Content-Type': content_type}

  http = httplib2.Http()
  response, content = http.request(
      endpoint,
      'POST',
      body=body,
      headers=headers,
  )

  if response.status < 300:
    if response.status == 204:
      return response, {}
    return response, json.loads(content.decode('utf-8'))
  else:
    raise errors.HttpError(response, content, uri=endpoint)


def _do_upload_attachment(policies: dict, file: resources.File) -> str:
  params = policies['form']
  params['file'] = file
  response, _ = _post_s3_request(
      policies['attachment']['endpoint'],
      params,
  )
  return urllib.parse.unquote(response['location'], encoding='utf-8')


def upload_attachment(client: EsaClient,
                      team_name: str,
                      file: Union[str, resources.File],
                      force_upload=False) -> str:
  if isinstance(file, str):
    file = resources.File(file)

  cache_key = f'{team_name}_{file.hash()}'
  cached_url = CACHE_STORAGE.get(cache_key)
  if cached_url and not force_upload:
    return cached_url

  policies = _fetch_attachment_policies(client, team_name, file)
  resource_url = _do_upload_attachment(policies, file)
  CACHE_STORAGE.set(cache_key, resource_url)
  return resource_url


def upload_and_render_table(client: EsaClient,
                            team_name: str,
                            df: pd.DataFrame,
                            force_upload=False,
                            minify_markdown=True) -> str:
  renderer = embedding.Renderer()

  def render_if_file(value):
    if isinstance(value, resources.File):
      url = upload_attachment(client, team_name, value, force_upload)
      return renderer.render(value, url)
    return value

  df = df.applymap(render_if_file)
  md = df.to_markdown()

  if minify_markdown:
    md = table.minify_markdown_table(md)

  return md
