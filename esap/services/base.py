import abc

from esap.base import BaseClient


class Service(abc.ABC):

  def __init__(self, client: BaseClient):
    self.client = client
