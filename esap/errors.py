import json


class Error(Exception):
  """Base error for this module."""

  pass


class HttpError(Error):
  """HTTP data was invalid or unexpected."""

  def __init__(self, response, content, uri=None):
    self.response = response
    if not isinstance(content, bytes):
      raise TypeError("HTTP content should be bytes")
    self.content = content
    self.uri = uri
    self.error_details = ""
    self.reason = self._get_reason()

  @property
  def status_code(self):
    """Return the HTTP status code from the response content."""
    return self.response.status

  def _get_reason(self):
    """Calculate the reason for the error from the response content."""
    reason = self.response.reason
    try:
      try:
        data = json.loads(self.content.decode("utf-8"))
      except json.JSONDecodeError:
        # In case it is not json
        data = self.content.decode("utf-8")
      if isinstance(data, dict):
        reason = data["error"]
        if "error_description" in data:
          self.error_details = data["error_description"]
        elif "message" in data:
          self.error_details = data["message"]
        else:
          self.error_details = data
      else:
        self.error_details = data
    except (ValueError, KeyError, TypeError):
      pass
    if reason is None:
      reason = ""
    return reason.strip()

  def __repr__(self):
    if self.error_details:
      return '<HttpError %s when requesting %s returned "%s". Details: "%s">' % (
          self.response.status,
          self.uri,
          self.reason,
          self.error_details,
      )
    elif self.uri:
      return '<HttpError %s when requesting %s returned "%s">' % (
          self.response.status,
          self.uri,
          self.reason,
      )
    else:
      return '<HttpError %s "%s">' % (self.response.status, self.reason)

  __str__ = __repr__
