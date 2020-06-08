from __future__ import annotations

from typing import TYPE_CHECKING


import distutils.dir_util
import os
from .pkginfo import PkgInfo
from . import package
from .db import Database
from .consts import ROOT_DIR, DBFILE

if TYPE_CHECKING:
    from typing import Optional, List


class FileConflictError(Exception):
    pass


def install(path: str) -> PkgInfo:
    pkginfo, pkgdir = package.unpack(path)
    for root, dirs, files in os.walk(pkgdir):
        for file in files:
            fpath = os.path.join(root, file)
            if os.path.exists(fpath[len(pkgdir) + 1:]):
                raise FileConflictError(fpath[len(pkgdir) + 1:])
    distutils.dir_util.copy_tree(pkgdir, ROOT_DIR)
    db = Database(DBFILE)
    db.add(pkginfo)
    db.commit()
    return pkginfo


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
