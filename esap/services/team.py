from __future__ import annotations

import json
from typing import Union
import urllib.parse

import httplib2
import pandas as pd
import tqdm

from esap import errors
from esap import resources
from esap import storage
from esap.base import BaseClient
from esap.markdown import embedding
from esap.markdown import table
from esap.services import base

CACHE_STORAGE = storage.LocalFileStorage('~/.esap/attachments_cache')

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


class TeamService(base.Service):

  def __init__(self, client: BaseClient, team_name: str):
    super(TeamService, self).__init__(client)
    self.team_name = team_name

  def upload_attachment(self,
                        file: Union[str, resources.File],
                        force_upload=False) -> str:
    if isinstance(file, str):
      file = resources.File(file)

    cache_key = f'{self.team_name}:{file.name}:{file.hash()}'
    cached_url = CACHE_STORAGE.get(cache_key)
    if cached_url and not force_upload:
      return cached_url

    policies = self._fetch_attachment_policies(file)
    resource_url = _do_upload_attachment(policies, file)
    CACHE_STORAGE.set(cache_key, resource_url)
    return resource_url

  def upload_and_render_table(self,
                              df: pd.DataFrame,
                              force_upload=False,
                              minify_markdown=True) -> str:
    num_files = 0
    for _, row in df.iterrows():
      for _, value in row.items():
        if isinstance(value, resources.File):
          num_files += 1

    if num_files > 0:
      with tqdm.tqdm(total=num_files) as pbar:

        def render_if_file(value):
          if not isinstance(value, resources.File):
            return value
          pbar.set_description(f'Uploading {value.name}')
          url = self.upload_attachment(value, force_upload)
          pbar.update(1)
          return embedding.render(value, url)

        df = df.applymap(render_if_file)

    md = df.to_markdown()

    if minify_markdown:
      md = table.minify_markdown_table(md)

    return md

  def _fetch_attachment_policies(self, file: resources.File):
    params = {
        'type': file.mimetype,
        'name': file.name,
        'size': file.size,
    }
    response = self.client.post_request(
        f'v1/teams/{self.team_name}/attachments/policies',
        body=params,
    )
    return response
