from __future__ import annotations

from typing import TYPE_CHECKING

import os
import sqlite3
from bap.consts import REPO_DIR
from bap.pkginfo import PkgInfo, Version
from bap.repo.sync import get_repositories, Repository

if TYPE_CHECKING:
    from typing import Optional, List


class PackageNotFoundError(Exception):
    pass


# TODO: add multi-repository support
# TODO: add version to file
# TODO: move search to function
def get_download_url(pkgname: str) -> str:
    founds: List[Repository] = []
    for repo in get_repositories():
        conn = sqlite3.connect(os.path.join(REPO_DIR, repo.name + '.db'))
        cur = conn.cursor()
        res = cur.execute(
            'SELECT name, desc, version FROM packages WHERE name = ?', (pkgname,)).fetchone()
        if res:
            founds.append(repo)
    if not founds:
        raise PackageNotFoundError(f'package {pkgname} not found')
    return os.path.join(founds[0].url_packages_root, pkgname) + '.bap'

def get_available_packages() -> List[PkgInfo]:
    packages: List[PkgInfo] = []
    for repo in get_repositories():
        conn = sqlite3.connect(os.path.join(REPO_DIR, repo.name + '.db'))
        cur = conn.cursor()
        res = cur.execute(
            'SELECT name, desc, version FROM packages').fetchall()
        for name, desc, version in res:
            packages.append(PkgInfo(
                name=name,
                desc=desc,
                version=Version.from_string(version)
            ))  # TODO: add another info to database
    return packages

