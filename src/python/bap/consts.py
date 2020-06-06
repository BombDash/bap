import os

try:
    import ba  # type: ignore # FIXME
    ROOT_DIR = ba.app.python_directory_user
except (ImportError, AttributeError):  # Running not from BallisticaCore, just test
    _envval = os.getenv('HOME')
    assert _envval
    ROOT_DIR = os.path.join(_envval, '.bap')


DBFILE = 'bap.db'
REPO_DIR = os.path.join(ROOT_DIR, '.baprepos')
CACHE_DIR = os.path.join(ROOT_DIR, '.bapcache')
os.makedirs(REPO_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
