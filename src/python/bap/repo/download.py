from __future__ import annotations

from typing import TYPE_CHECKING

import os
import urllib.request
from bap.repo.search import get_download_url
from bap.consts import CACHE_DIR
import datetime


if TYPE_CHECKING:
    from typing import Optional, List


def _download(url: str, dest: str, progress: bool = False) -> None:
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler())
    data = opener.open(url)
    nbytes = 0
    length = data.length
    last_info_time = int(datetime.datetime.now().timestamp())
    with open(dest, 'wb') as f:
        shatter = data.read(1024**2)
        while shatter:
            nbytes += f.write(shatter)
            if progress and last_info_time != int(datetime.datetime.now().timestamp()):
                last_info_time = int(datetime.datetime.now().timestamp())
                yield (100 * nbytes // length)
            shatter = data.read(1024)
        f.close()


def download(pkgname: str, progress: bool = False) -> None:
    url = get_download_url(pkgname)
    yield from _download(url, os.path.join(CACHE_DIR, pkgname + '.bap'), progress=progress)
