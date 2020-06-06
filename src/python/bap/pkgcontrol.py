from __future__ import annotations

from typing import TYPE_CHECKING


import os
import distutils.dir_util
from . import package
from .db import Database
from .consts import ROOT_DIR, DBFILE

if TYPE_CHECKING:
    from typing import Optional, List


def install(path: str) -> None:
    pkginfo, pkgdir = package.unpack(path)
    db = Database(DBFILE)
    db.add(pkginfo)
    db.commit()
    distutils.dir_util.copy_tree(pkgdir, ROOT_DIR)


def uninstall(name: str) -> None:
    db = Database(DBFILE)
    pkginfo = db.query(name, with_files=True)
    assert pkginfo.files
    for file in pkginfo.files:
        if os.path.exists(ROOT_DIR + file):
            os.remove(ROOT_DIR + file)
        else:
            print(f'warning: bap: file not found: {file}')
    db.remove(name)
    db.commit()
