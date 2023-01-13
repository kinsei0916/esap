import dataclasses
import hashlib
import mimetypes
import os
from typing import Union


def _guess_mimetype(path: str):
  mimetype, _ = mimetypes.guess_type(path)
  if mimetype is None:
    mimetype = 'application/octet-stream'
  return mimetype


@dataclasses.dataclass
class File:
  path: str

  # Generated automatically in __post_init__.
  mimetype: str = dataclasses.field(init=False)
  name: str = dataclasses.field(init=False)
  size: int = dataclasses.field(init=False)

  # Cached hash value.
  cached_hash: Union[str, None] = None

  def __post_init__(self):
    self.path = os.path.abspath(os.path.expanduser(self.path))
    self.mimetype = _guess_mimetype(self.path)
    self.name = os.path.basename(self.path)
    self.size = os.path.getsize(self.path)

  def hash(self):
    if self.cached_hash is None:
      self.cached_hash = hashlib.sha256(self.read()).hexdigest()
    return self.cached_hash

  def read(self):
    with open(self.path, 'rb') as f:
      return f.read()
