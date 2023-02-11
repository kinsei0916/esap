import re

_MAX_DIVIDER_LENGTH = 8


def minify_markdown_table(md: str) -> str:
  # Remove extra spaces around cells
  md = re.sub(r'\| *', '| ', md)
  md = re.sub(r' *\|', ' |', md)
  lines = md.splitlines()
  lines = [line.strip() for line in lines]
  if len(lines) > 1:
    # Limit the length of divider
    pattern = fr'-{{{_MAX_DIVIDER_LENGTH},}}'
    lines[1] = re.sub(pattern, '-' * _MAX_DIVIDER_LENGTH, lines[1])
  md = '\n'.join(lines)
  return md
