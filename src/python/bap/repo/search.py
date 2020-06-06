from __future__ import annotations

from typing import TYPE_CHECKING

import os
from .sync import get_repositories

if TYPE_CHECKING:
    from typing import Optional, List


# TODO: add multi-repository support
# TODO: add version to file
def get_download_url(pkgname: str) -> str:
    repo = get_repositories()[0]
    return os.path.join(repo.url_packages_root, pkgname) + '.bap'
