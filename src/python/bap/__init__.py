"""General bapman library. Provides API for package management"""

from .pkginfo import PkgInfo, Person, Version
from .package import pack as genpkg, unpack as extract_pkg
from .pkgcontrol import install, uninstall
from .db import Database
from . import repo

version = Version(0, 3, 2, 'dev')
