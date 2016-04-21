import json
import logging
import os
from pathlib import Path
from urllib.request import urlopen, Request
 
logger = logging.getLogger(__name__)
 
def get_links(client_id):
   headers = {'Authorization': 'Client-ID {}'.format(client_id)}
   req = Request('https://api.imgur.com/3/gallery/', headers=headers, method='GET')
   with urlopen(req) as resp:
       data = json.loads(resp.readall().decode('utf-8'))
   return map(lambda item: item['link'], data['data'])
 
def download_link(directory, link):
   logger.info('Downloading %s', link)
   download_path = directory / os.path.basename(link)
   with urlopen(link) as image, download_path.open('wb') as f:
       f.write(image.readall())
 
def setup_download_dir():
   download_dir = Path('images')
   if not download_dir.exists():
       download_dir.mkdir()
   return download_dir