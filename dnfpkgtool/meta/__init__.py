import json
from pathlib import Path

from loguru import logger

keywords = []
keyword_path = Path('pvfKeywords.json')
if keyword_path.exists():
    with keyword_path.open() as f:
        try:
            keywords = json.load(f)
        except json.decoder.JSONDecodeError:
            logger.error('Could not load keywords file')

keywords_dict = {}
keywords_dict_path = Path('pvfKeywordsDict.json')
if keywords_dict_path.exists():
    with keywords_dict_path.open() as f:
        try:
            keywords_dict = json.load(f)
        except json.decoder.JSONDecodeError:
            logger.error('Could not load keywords dict file')
