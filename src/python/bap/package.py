from __future__ import annotations

from typing import TYPE_CHECKING

import os
import shutil
import zipfile
import tempfile
import traceback

from .pkginfo import PkgInfo, Person, Version


if TYPE_CHECKING:
    from typing import Optional, List, Any, Dict, Sequence, Union, Tuple


class PkgInfoNotFound(Exception):
    pass


def _zipdir(path: str, zf: zipfile.ZipFile) -> None:
    """Add directory to ZipFile"""
    lastdir = os.getcwd()
    os.chdir(path)
    for root, dirs, files in os.walk('.'):
        for file in files:
            zf.write(os.path.join(root, file))
    os.chdir(lastdir)


def _pack(path: str, output_path: str) -> None:
    with zipfile.ZipFile(output_path, 'w') as zf:
        _zipdir(path, zf)


def gen_pkginfo(pkginfo: PkgInfo) -> str:
    data = '# This file automatically generated by BAP. See https://github.com/Dliwk/bap for details\n'
    data += f'name = {pkginfo.name}\n'
    data += f'version = {pkginfo.version.to_string()}\n'
    data += f'desc = {pkginfo.desc}\n'
    data += f'depends = {" ".join(pkginfo.depends)}\n'
    data += f'author = {pkginfo.author.to_string() if pkginfo.author else "nobody <nobody@example.com>"}\n'
    data += f'maintainer = {pkginfo.maintainer.to_string() if pkginfo.maintainer else "nobody <nobody@example.com>"}\n'

    return data


def pack(dirpath: str, output_path: str) -> None:
    pkginfopath = os.path.join(dirpath, 'pkginfo.py')
    if not os.path.exists(pkginfopath):
        raise PkgInfoNotFound('pkginfo.py file not found')
    f = open(pkginfopath)
    data = f.read()
    f.close()
    values: Dict[str, Any] = {}
    exec(data, {'PkgInfo': PkgInfo, 'Version': Version, 'Person': Person}, values)

    pkginfo = values['pkginfo']
    pkginfo_data = gen_pkginfo(pkginfo)
    builddir = tempfile.mkdtemp()
    buildpkg = os.path.join(builddir, dirpath + '.pkgdir')
    if os.path.exists(buildpkg):
        shutil.rmtree(buildpkg)
    shutil.copytree(dirpath, buildpkg)
    os.remove(buildpkg + '/pkginfo.py')
    f = open(buildpkg + '/PKGINFO', 'w')
    f.write(pkginfo_data)
    f.close()
    _pack(buildpkg, output_path)


def _parse_pkginfo(data: str) -> Dict[str, str]:
    obj = {}
    for line in data.split('\n'):
        if line.strip().startswith('#') or not line.strip():
            continue
        key, val = map(lambda x: x.strip(), line.split('=', 1))
        obj[key] = val
    return obj


def parse_pkginfo(data: str) -> PkgInfo:
    obj: Dict[str, str] = _parse_pkginfo(data)
    name: str = obj['name']
    version: Version = Version.from_string(obj['version'])
    depends: List[str] = obj['depends'].split()
    desc: str = obj['desc']
    author: Person = Person.from_string(obj['author'])
    maintainer: Person = Person.from_string(obj['maintainer'])
    return PkgInfo(
        name=name,
        version=version,
        depends=depends,
        desc=desc,
        author=author,
        maintainer=maintainer)


def unpack(path: str) -> Tuple[PkgInfo, str]:
    with zipfile.ZipFile(path, 'r') as zf:
        pkginfo_file = zf.open('PKGINFO', 'r')
        pkginfo_data = pkginfo_file.read().decode('utf-8')
        pkginfo_file.close()
        pkginfo = parse_pkginfo(pkginfo_data)
        pkgdir = tempfile.mkdtemp()
        zf.extractall(pkgdir)
        os.remove(os.path.join(pkgdir, 'PKGINFO'))
        pkginfo.files = []
        current_dir = os.getcwd()
        os.chdir(pkgdir)
        for root, dirs, files in os.walk('.'):
            for file in files:
                pkginfo.files.append(os.path.join(root, file)[1:])
        os.chdir(current_dir)
        return pkginfo, pkgdir
