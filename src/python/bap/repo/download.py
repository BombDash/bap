from __future__ import annotations

from typing import TYPE_CHECKING

import os
import urllib.request
from bap.repo.search import get_download_url
from bap.consts import CACHE_DIR


if TYPE_CHECKING:
    from typing import Optional, List


def _download(url: str, dest: str) -> None:
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler())
    data = opener.open(url)
    with open(dest, 'wb') as f:
        shatter = data.read(1024)
        while shatter:
            f.write(shatter)
            shatter = data.read(1024)
        f.close()


def download(pkgname: str) -> None:
    url = get_download_url(pkgname)
    _download(url, os.path.join(CACHE_DIR, pkgname + '.bap'))
