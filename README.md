# Esap

Esap is a set of utilities to speed things up for writing posts on [esa.io](https://esa.io/).  
Currently being developed for my personal use.

## Installation

You can install esap with `pip`.

```bash
$ git clone https://github.com/kon72/esap.git
$ cd esap
$ pip install .
```

## Quickstart

1. Go to [esa.io](https://esa.io/) and login to your team.
1. Click **SETTINGS** on the left side of the screen.
1. Select **User Settings** > **Applications** from the left pane.
1. Click **Register new application**.
1. Fill in the form like below and save it.

    | Name | Value |
    | --- | --- |
    | Name | esap |
    | Homepage URL | <https://github.com/kon72/esap> |
    | Redirect URI | urn:ietf:wg:oauth:2.0:oob <br> http://localhost:8080/ |

1. Click **esap** that you just created.
1. You will see the **Client ID** and **Client Secret**. Now run the following command. Note that you need to replace `<your client id>` and `<your client secret>` with the values you just got.

    ```bash
    $ mkdir -p ~/.esap
    $ touch ~/.esap/client_secrets
    $ chmod 600 ~/.esap/client_secrets
    $ echo "client_id=<your client id>" >> ~/.esap/client_secrets
    $ echo "client_secret=<your client secret>" >> ~/.esap/client_secrets
    ```

1. Run the following command and you will be asked to open the URL in your browser. After you click **Authorize**, you will be given a code. Copy and paste it to the terminal and you are done!

    ```bash
    $ python
    >>> import esap
    >>> client = esap.EsaClient()
    ```

## Usage

### Upload images, audio, video, etc

You can upload any file to your team's storage with `upload_attachment` method.

```python
import esap

client = esap.EsaClient()
team = client.team_service('your_team_name')
file = esap.File('path/to/file')
url = team.upload_attachment(file)
print(url)
```

The output will be:

```
https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/...
```

### Render uploaded files as markdown

You can render uploaded files in the form of markdown text with `render_attachment` method.

```python
import esap

client = esap.EsaClient()
team = client.team_service('your_team_name')
file = esap.File('path/to/an/image.png')
url = team.upload_attachment(file)
markdown = esap.markdown.render_attachment(file, url)
print(markdown)
```

The output will be:

```
<img alt="image.png" src="https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/...">
```

### Upload multiple files and render them in a markdown table

This is where esap shines. You can upload all files listed in pandas DataFrame and render it as a markdown table with `upload_and_render_table` method.

```python
import collections
import os

import pandas as pd

import esap

animal_names = ['dog', 'cat']
filter_names = ['original', 'grayscale']
data = collections.defaultdict(dict)
for filter_name in filter_names:
  for animal_name in animal_names:
    path = os.path.join('assets', filter_name, f'{animal_name}.jpg')
    data[filter_name][animal_name] = esap.File(path)
df = pd.DataFrame(data)

client = esap.EsaClient()
team = client.team_service('your_team_name')
markdown = team.upload_and_render_table(df)
print(markdown)
```

The output will be:

```text
| | original | grayscale |
| :---- | :-------- | :-------- |
| dog | <img alt="dog.jpg" src="https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/uploads/production/attachments/20297/2023/02/12/84817/c8ffaec1-565b-4676-a8bb-2a1dfb635744.jpg"> | <img alt="dog.jpg" src="https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/uploads/production/attachments/20297/2023/02/12/84817/604f5dea-d72b-4e97-8fe6-dcc7fbf39d4d.jpg"> |
| cat | <img alt="cat.jpg" src="https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/uploads/production/attachments/20297/2023/02/12/84817/ea920239-4427-4003-83a4-dd55c83af5e2.jpg"> | <img alt="cat.jpg" src="https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/uploads/production/attachments/20297/2023/02/12/84817/9e57f7af-0d4d-4379-8db4-9f360446ca32.jpg"> |
```

The table will be rendered like this:

| | original | grayscale |
| :---- | :-------- | :-------- |
| dog | <img alt="dog.jpg" src="https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/uploads/production/attachments/20297/2023/02/12/84817/c8ffaec1-565b-4676-a8bb-2a1dfb635744.jpg"> | <img alt="dog.jpg" src="https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/uploads/production/attachments/20297/2023/02/12/84817/604f5dea-d72b-4e97-8fe6-dcc7fbf39d4d.jpg"> |
| cat | <img alt="cat.jpg" src="https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/uploads/production/attachments/20297/2023/02/12/84817/ea920239-4427-4003-83a4-dd55c83af5e2.jpg"> | <img alt="cat.jpg" src="https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/uploads/production/attachments/20297/2023/02/12/84817/9e57f7af-0d4d-4379-8db4-9f360446ca32.jpg"> |
