import abc
import os


class BaseStorage(abc.ABC):

  @abc.abstractmethod
  def get(self, key: str):
    pass

  @abc.abstractmethod
  def set(self, key: str, value: str):
    pass

  @abc.abstractmethod
  def delete(self, key: str):
    pass

  @abc.abstractmethod
  def set_from_dict(self, data: dict[str, str]):
    pass

  @abc.abstractmethod
  def to_dict(self) -> dict[str, str]:
    pass


class LocalFileStorage(BaseStorage):

  def __init__(self, path: str, secure=False):
    self.path = os.path.abspath(os.path.expanduser(path))
    self.secure = secure
    self.data = self._read()

  def get(self, key: str):
    return self.data.get(key)

  def set(self, key: str, value: str):
    if key in self.data or self.secure:
      self.data[key] = value
      self._write(self.data)
    else:
      self.data[key] = value
      self._append(key, value)

  def delete(self, key: str):
    del self.data[key]
    self._write(self.data)

  def set_from_dict(self, data: dict[str, str]):
    self.data = dict(data)
    self._write(self.data)

  def to_dict(self) -> dict[str, str]:
    return dict(self.data)

  def _get_opener(self):
    if not self.secure:
      return None

    def opener(path, flags):
      flags |= os.O_NOFOLLOW
      return os.open(path, flags, 0o600)

    return opener

  def _read(self) -> dict[str, str]:
    data = {}
    try:
      with open(self.path, 'r', encoding='utf-8',
                opener=self._get_opener()) as f:
        lines = f.readlines()
      for line in lines:
        key, value = line.split('=', 1)
        data[key] = value.rstrip('\n')
    except FileNotFoundError:
      return {}

    return data

  def _write(self, data: dict[str, str]):
    if self.secure:
      try:
        os.remove(self.path)
      except FileNotFoundError:
        pass

    os.makedirs(os.path.dirname(self.path), exist_ok=True)
    with open(self.path, 'w', encoding='utf-8', opener=self._get_opener()) as f:
      for key, value in data.items():
        if value is not None:
          f.write(f'{key}={value}\n')

  def _append(self, key: str, value: str):
    assert not self.secure
    os.makedirs(os.path.dirname(self.path), exist_ok=True)
    with open(self.path, 'a', encoding='utf-8', opener=self._get_opener()) as f:
      f.write(f'{key}={value}\n')


class InMemoryStorage(BaseStorage):

  def __init__(self, initial_data: dict[str, str] = {}):
    self.data = initial_data

  def get(self, key: str):
    return self.data.get(key)

  def set(self, key: str, value: str):
    self.data[key] = value

  def delete(self, key: str):
    del self.data[key]

  def set_from_dict(self, data: dict[str, str]):
    self.data = dict(data)

  def to_dict(self) -> dict[str, str]:
    return dict(self.data)
