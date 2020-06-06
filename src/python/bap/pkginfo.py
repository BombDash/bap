from __future__ import annotations

from typing import TYPE_CHECKING

# use it instead? but what about android devices?
# from packaging.version import Version

if TYPE_CHECKING:
    from typing import Optional, List


class Version:
    def __init__(self, major: int, minor: int, patch: int,
                 prerelease: Optional[str] = None, buildinfo: Optional[str] = None) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.buildinfo = buildinfo

    def to_string(self) -> str:
        return f'{self.major}.{self.minor}.{self.patch}' \
               f'{"-" + self.prerelease if self.prerelease else ""}' \
               f'{"+" + self.buildinfo if self.buildinfo else ""}'

    @classmethod
    def from_string(cls, string: str) -> Version:
        major, minor, patch = string.split('.')
        patch = patch.split('-', 1)[0]
        prerelease = string.split('-', 1)[1].split('+', 1)[0] if '-' in string else None
        buildinfo = string.split('+', 1)[1] if '+' in string else None
        return Version(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease,
            buildinfo=buildinfo)

    def __repr__(self) -> str:
        return f'<bapack.Version object {self.to_string()}>'



class Person:
    def __init__(self, fullname: str, email: str, website: Optional[str] = None) -> None:
        self.fullname = fullname
        self.email = email
        self.website = website

    @classmethod
    def from_string(cls, string: str) -> Person:
        fullname: str = string.split('<', 1)[0].strip()
        email: str = string.split('<', 1)[1].split('>', 1)[0].strip()
        website: Optional[str]
        try:
            website = string.split('(', 1)[1].split(')', 1)[0].strip()
        except IndexError:
            website = None
        return Person(fullname=fullname, email=email, website=website)

    def to_string(self) -> str:
        return f'{self.fullname} <{self.email}>' + (f' {self.website}' if self.website else '')


class PkgInfo:
    def __init__(self,
                 name: str,
                 version: Version,
                 desc: str,
                 depends: Optional[List[str]] = None,  # List[Union[str, PkgInfo]],  # FIXME
                 author: Optional[Person] = None,
                 maintainer: Optional[Person] = None,
                 files: Optional[List[str]] = None) -> None:
        self.name = name
        self.version = version
        self.depends = depends if depends else []
        self.desc = desc
        self.author = author
        self.maintainer = maintainer
        self.files = files

    def to_string(self) -> str:
        return f'{self.name}-{self.version.to_string()}'
