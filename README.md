# BAP and Bapman
#### [Ballistica](https://ballistica.net) mods packager library
#### BAP Manager - GUI front-end for BAP 

### What is it?
**For user:**
Easy way to download new mods and install updates

**For developers:**
Easy way to distribute mods and share updates

### Build
1. Clone or download this repository
2. Run `./configure.py sync`; it will clone Ballistica repository and something to prepare build
3. Run `./configure.py build` and wait for debug build finish.
Profit!

### How to make package? How to install it?
BAP provides a simple API for packaging control. Here are some useful methods.

`bapack.install("<path_to_package>")` - install package from file (e.g. `test.bap`)

`bapack.uninstall("<pkg_name>")` - uninstall package **<pkg_name>**

`bapack.genpkg("<path_to_package_dir>")` - make package from directory

A word about package directory format. It will just copyed in Ballistica user mods directory, all package files will saved to database. BAP want to get package information - in root package directory must be **pkginfo.py** script. Example:
```python
import datetime
pkginfo = PkgInfo(
    name="test",
    version=Version.from_string(f'0.1.5-dev+{datetime.datetime.now().timestamp()}'),
    desc="test package",
    author=Person.from_string('Test Person <testperson@example.com>'),
    maintainer=Person.from_string('Test Person <testperson@example.com>'))
# This script must define pkginfo variable - instance of PkgInfo class
```

### Repositories
File named **repolist** lives in BAP repository directory i.e. `<User mods folder>/.baprepos/repolist`

#### Example of repolist file
```sh
# bap repositories list
#
# <name> <url_repo_database> <url_packages_root>
# My local repository. I use it for testing my packages
localrepo http://localhost:8000/repo.db http://localhost:8000

# My global repository. It contains release builds.
supermodder https://example.com/supermodder/baprepo/repo.db https://example.com/supermodder/baprepo/packages
```