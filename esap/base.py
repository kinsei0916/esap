import abc


class BaseClient(abc.ABC):

  def get_request(self, endpoint: str, query_params=None, headers=None):
    pass

  def post_request(self, endpoint: str, body=None, headers=None):
    pass
