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


class ConfigureApp:
    """Application for BAP building"""

    _targets: List[Callable[["ConfigureApp"], None]]

    def __init__(self, python_path: str, mypy_config_file: str, manifest_path: str,
                 srcdir: str, ballistica_path: str, git_path: str, make_path: str,
                 ballistica_repo_url: str, tooldir: str, tool_manifest_path: str,
                 pylint_rcfile: str) -> None:
        self._python_path = python_path
        self._mypy_config_file = mypy_config_file
        self._pylint_rcfile = pylint_rcfile
        self._manifest_path = manifest_path
        self._srcdir = srcdir
        self._ballistica_path = ballistica_path
        self._git_path = git_path
        self._ballistica_repo_url = ballistica_repo_url
        self._tooldir = tooldir
        self._tool_manifest_path = tool_manifest_path
        self._make_path = make_path
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
                del dirs  # unused.
                for filename in files:
                    if filename.endswith('.py'):
                        projectfiles.append(os.path.join(root, filename))
            if not initial:
                newfiles = set(projectfiles) - set(self._project_files)
                if newfiles:
                    print(f'New project files detected: {", ".join(newfiles)}!')
                else:
                    print('Project manifest are up to date!')

            manifest.write(json.dumps(projectfiles, indent=2))

    def _update_tool_manifest(self, initial: bool = False) -> None:
        with open(self._tool_manifest_path, 'w') as manifest:
            toolfiles: List[str] = []
            for root, dirs, files in os.walk(self._tooldir):
                del dirs  # unused.
                for filename in files:
                    if filename.endswith('.py'):
                        toolfiles.append(os.path.join(root, filename))
            toolfiles.append(os.path.basename(sys.argv[0]))
            if not initial:
                newfiles = set(toolfiles) - set(self._tool_files)
                if newfiles:
                    print(f'New tool files detected: {", ".join(newfiles)}!')
                else:
                    print('Tool manifest are up to date!')

            manifest.write(json.dumps(toolfiles, indent=2))

    def _sync_ba(self, check: bool = True) -> None:
        print('Syning git repository...')
        if not os.path.exists(os.path.join(self._ballistica_path, '.git')):
            os.makedirs(os.path.dirname(self._ballistica_path), exist_ok=True)
            subprocess.run([
                self._git_path, 'clone', self._ballistica_repo_url,
                self._ballistica_path
            ], check=check)
        else:
            subprocess.run([
                self._git_path, '-C', self._ballistica_path, 'pull'
            ], check=check)

    def _remove_broken_symlinks(self) -> None:
        for root, dirs, files in reversed(list(os.walk(os.path.join(self._ballistica_path,
                                                                    'assets/src/ba_data')))):
            for dest in files:
                dest = os.path.join(root, dest)
                if not os.path.exists(dest) and os.path.islink(dest):
                    print(f'removing broken symlink {dest}...')
                    os.remove(dest)
            for directory in dirs:
                directory = os.path.join(root, directory)
                if not os.listdir(directory):
                    print(f'removing empty directory {directory}...')
                    os.rmdir(directory)


    def _create_symlinks(self) -> None:
        print('Creating symlinks...')
        self._remove_broken_symlinks()
        for projectfile in self._project_files:
            assert projectfile.startswith(self._srcdir)
            projectfile = projectfile[len(self._srcdir) + 1:]
            dest = os.path.join(self._ballistica_path, 'assets/src/ba_data',
                                projectfile)
            if not os.path.exists(dest):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                os.symlink(os.path.abspath(os.path.join(
                    self._srcdir, projectfile)), dest)
                print(f'Created symlink to {dest}')

    def _run_ba_update(self, check: bool = True) -> None:
        print('Updating Ballistica source...')
        subprocess.run([
                self._make_path, 'update'
            ], cwd=self._ballistica_path, check=check)


    def _mypy(self, filenames: List[str], check: bool, use_ba_tools: bool = True) -> None:
        if use_ba_tools:
            subprocess.run([
                self._make_path, 'mypy'
            ], cwd=self._ballistica_path, check=check)
        else:
            try:
                subprocess.run([
                    self._python_path, '-m', 'mypy', '--pretty', '--config-file',
                    self._mypy_config_file,
                ] + filenames, check=check)
            except subprocess.CalledProcessError:
                print('Mypy: fail')
            else:
                print('Mypy: success')

    def _pylint(self, filenames: List[str], check: bool, use_ba_tools: bool = True) -> None:
        if use_ba_tools:
            subprocess.run([
                self._make_path, 'pylint'
            ], cwd=self._ballistica_path, check=check)
        else:
            try:
                subprocess.run([
                    self._python_path, '-m', 'pylint', '--rcfile',
                    self._pylint_rcfile, '--output-format=colorized'
                ] + filenames, check=check)
            except subprocess.CalledProcessError:
                print('Pylint: fail')
            else:
                print('Pylint: success')
    
    def _build(self, buildtype: str, check: bool = True) -> None:
        subprocess.run([
            self._make_path, f'prefab-{buildtype}-build'
        ], cwd=self._ballistica_path, check=check)
        

    def mypy(self, check: bool = True) -> None:
        self._mypy(self._tool_files, check=check, use_ba_tools=False)
        self._mypy(self._project_files, check=check, use_ba_tools=True)

    def pylint(self, check: bool = True) -> None:
        self._pylint(self._tool_files, check=check, use_ba_tools=False)
        self._pylint(self._project_files, check=check, use_ba_tools=True)

    def update(self) -> None:
        self._update_manifest()
        self._update_tool_manifest()

    def sync(self) -> None:
        self._sync_ba()
        self._create_symlinks()
        self._run_ba_update()
    
    def build(self) -> None:
        self._build('debug')

    @staticmethod
    def parse_args(args: Sequence[CommandLineArgument]) -> None:
        targets = ('mypy', 'update', 'sync', 'pylint', 'build')
        assert __doc__
        parser = argparse.ArgumentParser(
            description=__doc__.split('\n')[0])
        parser.add_argument('target', choices=targets)
        parser.add_argument('--python-path', default=sys.executable)
        parser.add_argument('--git-path', default='git')
        parser.add_argument('--make-path', default='make')
        parser.add_argument('--manifest-path', default='.manifest.json')
        parser.add_argument('--tool-manifest-path', default='.manifest-tools.json')
        parser.add_argument('--srcdir', default='src')
        parser.add_argument('--tooldir', default='tools')
        parser.add_argument('--ballistica-path', default='build/ballistica')
        parser.add_argument('--ballistica-repo-url',
                             default='https://github.com/efroemling/ballistica.git')
        parser.add_argument('--mypy-config', default='config/mypy.ini', dest='mypy_config_file')
        parser.add_argument('--pylintrc', default='config/pylintrc', dest='pylint_rcfile')
        ns = parser.parse_args(args[1:])

        app = ConfigureApp(
            python_path=ns.python_path,
            mypy_config_file=ns.mypy_config_file,
            manifest_path=ns.manifest_path,
            srcdir=os.path.join(ns.srcdir),  # exclude / on path end
            ballistica_path=ns.ballistica_path,
            git_path=ns.git_path,
            ballistica_repo_url=ns.ballistica_repo_url,
            tooldir=ns.tooldir,
            tool_manifest_path=ns.tool_manifest_path,
            make_path=ns.make_path,
            pylint_rcfile=ns.pylint_rcfile)
        getattr(app, ns.target)()


if __name__ == '__main__':
    ConfigureApp.parse_args(sys.argv)
