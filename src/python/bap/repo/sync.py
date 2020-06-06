from __future__ import annotations

from typing import TYPE_CHECKING

import os
from dataclasses import dataclass
from bap.consts import REPO_DIR

if TYPE_CHECKING:
    from typing import Optional, List


def check_for_repolist() -> None:
    repolist_path = os.path.join(REPO_DIR, 'repolist')
    if not os.path.exists(repolist_path):
        with open(repolist_path, 'w') as f:
            f.write('# bap repositories list\n')
            f.write('#\n')
            f.write('# <name> <url_repo_database> <url_packages_root>\n')
            f.close()


@dataclass
class Repository:
    name: str
    url_repo_database: str
    url_packages_root: str


def get_repositories() -> List[Repository]:
    check_for_repolist()
    repositories: List[Repository] = []
    with open(os.path.join(REPO_DIR, 'repolist')) as f:
        for line in f.read().splitlines():
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            name, url_repo_database, url_packages_root = line.split()
            repositories.append(Repository(
                name=name,
                url_repo_database=url_repo_database,
                url_packages_root=url_packages_root
            ))
    return repositories



def sync() -> None:
    from bap.repo.download import _download as download_file
    repos = get_repositories()
    for repo in repos:
        download_file(repo.url_repo_database, os.path.join(REPO_DIR, repo.name + '.db'))
