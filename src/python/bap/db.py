from __future__ import annotations

from typing import TYPE_CHECKING

import os
import sqlite3

from .pkginfo import PkgInfo, Person, Version
from .consts import DBFILE


class Database:
    def __init__(self, path: str = DBFILE):
        self._dbfile = path
        _setup_requered = not os.path.exists(self._dbfile)
        self._connection = sqlite3.connect(self._dbfile)
        self._cursor = self._connection.cursor()

        if _setup_requered:
            self._dbinit()
    
    def _dbinit(self) -> None:
        self._cursor.execute("""CREATE TABLE packages(
            name varchar(20) PRIMARY KEY,
            desc varchar(100) NOT NULL,
            version varchar(30) NOT NULL
        );""")  # TODO: add depends
        self._cursor.execute("""CREATE TABLE files(
            path varchar(127) PRIMARY KEY,
            package INTEGER NOT NULL,
            FOREIGN KEY(package) REFERENCES packages (`name`)
        );""")
        # TODO: add default packages such as bap and ballisticacore
        # self._cursor.execute("""INSERT INTO packages(`name`, `desc`, version) VALUES
        #     ("bapack", "Ballistica mods packager", ?)""", (version.string(),))
        # for file in BAPACK_FILES:
        #     self._cursor.execute("""INSERT INTO files(path, package) VALUES
        #         (?, "bapack")""", (file,))

    
    def query(self, name: str, with_files: bool = False) -> PkgInfo:
        pkg = self._cursor.execute(
            'SELECT `name`, `version`, `desc` FROM packages WHERE `name` = ?', (name,)).fetchone()
        files = None
        if with_files:
            files = [i[0] for i in self._cursor.execute(
                'SELECT * FROM files WHERE files.package = ?', (name,)).fetchall()]
        return PkgInfo(
            name=pkg[0],
            version=Version.from_string(pkg[1]),
            desc=pkg[2],
            files=files)
    
    def installed(self):
        result = self._cursor.execute(
            'SELECT `name`, `version`, `desc` FROM packages').fetchall()
        for pkg in result:
            yield PkgInfo(
                name=pkg[0],
                version=Version.from_string(pkg[1]),
                desc=pkg[2],
                files=None)
    
    def add(self, pkginfo: PkgInfo) -> None:
        self._cursor.execute('INSERT INTO `packages` (name, desc, version) VALUES (?, ?, ?)',
                             (pkginfo.name, pkginfo.desc, pkginfo.version.to_string()))

        assert pkginfo.files is not None
        for file in pkginfo.files:
            self._cursor.execute('INSERT INTO `files` (path, package) VALUES (?, ?)',
                                 (file, pkginfo.name))

    def remove(self, name: str) -> None:
        self._cursor.execute('DELETE FROM `files` WHERE `package` = ?', (name,))
        self._cursor.execute('DELETE FROM `packages` WHERE `name` = ?', (name,))
    
    def commit(self) -> None:
        self._connection.commit()

    def __del__(self) -> None:
        self._cursor.close()
        self._connection.close()
