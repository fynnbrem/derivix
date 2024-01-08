import logging
import tempfile
from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Union, Optional

logging.basicConfig(level=logging.INFO)
TEMP = tempfile.TemporaryDirectory()
TEMP_PATH = Path(TEMP.name)
logging.info(f"Created temporary folder at: `{TEMP_PATH}`")