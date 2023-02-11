import abc

from lxml import html

from esap import resources


def _html_element_to_string(element: html.HtmlElement) -> str:
  temp = html.tostring(element)
  if isinstance(temp, bytes):
    temp = temp.decode('utf-8')
  return temp


class BaseRenderer(abc.ABC):

  @abc.abstractmethod
  def can_handle(self, mimetype: str) -> bool:
    pass

  @abc.abstractmethod
  def render(self, file: resources.File, url: str) -> str:
    pass


class ImageRenderer(BaseRenderer):

  def can_handle(self, mimetype: str) -> bool:
    return mimetype.startswith('image/')

  def render(self, file: resources.File, url: str) -> str:
    img = html.Element('img')
    img.set('alt', file.name)
    img.set('src', url)
    return _html_element_to_string(img)


class AudioRenderer(BaseRenderer):

  def can_handle(self, mimetype: str) -> bool:
    return mimetype.startswith('audio/')

  def render(self, file: resources.File, url: str) -> str:
    audio = html.Element('audio')
    audio.set('controls')
    audio.set('alt', file.name)
    audio.set('src', url)
    return _html_element_to_string(audio)


class VideoRenderer(BaseRenderer):

  def can_handle(self, mimetype: str) -> bool:
    return mimetype.startswith('video/')

  def render(self, file: resources.File, url: str) -> str:
    video = html.Element('video')
    video.set('controls')
    video.set('alt', file.name)
    video.set('src', url)
    return _html_element_to_string(video)


class DefaultRenderer(BaseRenderer):

  def can_handle(self, mimetype: str) -> bool:
    return True

  def render(self, file: resources.File, url: str) -> str:
    a = html.Element('a')
    a.set('href', url)
    a.text = file.name
    return _html_element_to_string(a)


_RENDERING_HANDLERS = [
    ImageRenderer(),
    AudioRenderer(),
    VideoRenderer(),
    DefaultRenderer(),
]


def render(file: resources.File, url: str) -> str:
  for renderer in _RENDERING_HANDLERS:
    if renderer.can_handle(file.mimetype):
      return renderer.render(file, url)
  raise RuntimeError(f'No renderer found for file: {file}')
