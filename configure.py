#!/usr/bin/env python3
"""Main script for BAP building"""
from __future__ import annotations

from typing import TYPE_CHECKING

import os
import sys
import json
import argparse
import subprocess

if TYPE_CHECKING:
    from typing import Sequence, List, Callable, TypeVar, NewType

    CommandLineArgument = TypeVar('CommandLineArgument', bound=str)


def target(function: Callable[["ConfigureApp"], None]) -> Callable[["ConfigureApp"], None]:
    setattr(function, '_is_target', True)

    return function



class ConfigureApp:
    """Application for BAP building"""

    _targets: List[Callable[["ConfigureApp"], None]]

    def __init__(self, python_path: str, mypy_config_file: str, manifest_path: str,
                 srcdir: str, ballistica_path: str, git_path: str,
                 ballistica_repo_url: str, tooldir: str, tool_manifest_path: str) -> None:
        self._python_path = python_path
        self._mypy_config_file = mypy_config_file
        self._manifest_path = manifest_path
        self._srcdir = srcdir
        self._ballistica_path = ballistica_path
        self._git_path = git_path
        self._ballistica_repo_url = ballistica_repo_url
        self._tooldir = tooldir
        self._tool_manifest_path = tool_manifest_path
        self._project_files: List[str]
        self._tool_files: List[str]

        self._get_project_files()
        self._get_tool_files()
    
    def _get_project_files(self) -> None:
        if not os.path.exists(self._manifest_path):
            self._update_manifest(initial=True)
        with open(self._manifest_path) as manifest:
            self._project_files = json.loads(manifest.read())
    
    def _get_tool_files(self) -> None:
        if not os.path.exists(self._tool_manifest_path):
            self._update_tool_manifest(initial=True)
        with open(self._tool_manifest_path) as manifest:
            self._tool_files = json.loads(manifest.read())
    
    def _update_manifest(self, initial: bool = False) -> None:
        with open(self._manifest_path, 'w') as manifest:
            projectfiles: List[str] = []
            for root, dirs, files in os.walk(self._srcdir):
                for filename in files:
                    if filename.endswith('.py'):
                        projectfiles.append(os.path.join(root, filename))
            if not initial:
                newfiles = set(projectfiles) - set(self._project_files)
                if newfiles:
                    print(f'New project files detected: {", ".join(newfiles)}!')
                else:
                    print(f'Project manifest are up to date!')

            manifest.write(json.dumps(projectfiles, indent=2))
    
    def _update_tool_manifest(self, initial: bool = False) -> None:
        with open(self._tool_manifest_path, 'w') as manifest:
            toolfiles: List[str] = []
            for root, dirs, files in os.walk(self._tooldir):
                for filename in files:
                    if filename.endswith('.py'):
                        toolfiles.append(os.path.join(root, filename))
            toolfiles.append(os.path.basename(sys.argv[0]))
            if not initial:
                newfiles = set(toolfiles) - set(self._tool_files)
                if newfiles:
                    print(f'New tool files detected: {", ".join(newfiles)}!')
                else:
                    print(f'Tool manifest are up to date!')

            manifest.write(json.dumps(toolfiles, indent=2))
    
    def _sync_ba(self) -> None:
        if not os.path.exists(os.path.join(self._ballistica_path, '.git')):
            os.makedirs(os.path.dirname(self._ballistica_path), exist_ok=True)
            subprocess.run([
                self._git_path, 'clone', self._ballistica_repo_url,
                self._ballistica_path
            ])
        else:
            subprocess.run([
                self._git_path, '-C', self._ballistica_path, 'pull'
            ])

    def _mypy(self, filenames: List[str], check: bool) -> None:
        try:
            result = subprocess.run([
                self._python_path, '-m', 'mypy', '--pretty', '--config-file',
                self._mypy_config_file,
            ] + filenames, check=check)
        except subprocess.CalledProcessError:
            print('Mypy: fail')
        else:
            print('Mypy: success')
    
    def mypy(self, check: bool = True) -> None:
        self._mypy(self._project_files + self._tool_files, check=check)
    
    def update(self) -> None:
        self._update_manifest()
        self._update_tool_manifest()
    
    def sync(self) -> None:
        self._sync_ba()

    @staticmethod
    def parse_args(args: Sequence[CommandLineArgument]) -> None:
        targets = ('mypy', 'update', 'sync')
        assert __doc__
        parser = argparse.ArgumentParser(
            description=__doc__.split('\n')[0])
        parser.add_argument('target', choices=targets)
        parser.add_argument('--python-path', default='python3')
        parser.add_argument('--git-path', default='git')
        parser.add_argument('--manifest-path', default='.manifest.json')
        parser.add_argument('--tool-manifest-path', default='.manifest-tools.json')
        parser.add_argument('--srcdir', default='src')
        parser.add_argument('--tooldir', default='tools')
        parser.add_argument('--ballistica-path', default='build/ballistica')
        parser.add_argument('--ballistica-repo-url',
                             default='https://github.com/efroemling/ballistica.git')
        parser.add_argument('--mypy-config', default='config/mypy.ini', dest='mypy_config_file')
        ns = parser.parse_args(args[1:])

        app = ConfigureApp(
            python_path=ns.python_path,
            mypy_config_file=ns.mypy_config_file,
            manifest_path=ns.manifest_path,
            srcdir=ns.srcdir,
            ballistica_path=ns.ballistica_path,
            git_path=ns.git_path,
            ballistica_repo_url=ns.ballistica_repo_url,
            tooldir=ns.tooldir,
            tool_manifest_path=ns.tool_manifest_path)
        getattr(app, ns.target)()


if __name__ == '__main__':
    ConfigureApp.parse_args(sys.argv)