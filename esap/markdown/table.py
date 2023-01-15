import re


def minify_markdown_table(md: str) -> str:
  md = re.sub(r'\| *', '| ', md)
  md = re.sub(r' *\|', ' |', md)
  md = re.sub(r' *\|', ' |', md)
  lines = md.splitlines()
  lines = [line.strip() for line in lines]
  lines[1] = re.sub(r'-+', '--------', lines[1])
  md = '\n'.join(lines)
  return md
