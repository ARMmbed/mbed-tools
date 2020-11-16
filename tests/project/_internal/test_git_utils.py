#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from pathlib import Path
from unittest import mock

import pytest

from mbed_tools.project.exceptions import VersionControlError
from mbed_tools.project._internal import git_utils


@pytest.fixture
def mock_repo():
    with mock.patch("mbed_tools.project._internal.git_utils.git.Repo") as repo:
        yield repo


@pytest.fixture
def mock_progress():
    with mock.patch("mbed_tools.project._internal.git_utils.ProgressReporter") as progress:
        yield progress


class TestClone:
    def test_returns_repo(self, mock_progress, mock_repo):
        url = "https://blah"
        path = Path()
        repo = git_utils.clone(url, path)

        assert repo is not None
        mock_repo.clone_from.assert_called_once_with(url, str(path), progress=mock_progress())

    def test_raises_when_clone_fails(self):
        with pytest.raises(VersionControlError):
            git_utils.clone("", Path())


class TestInit:
    def test_returns_initialised_repo(self, mock_repo):
        repo = git_utils.init(Path())

        assert repo is not None
        mock_repo.init.assert_called_once_with(str(Path()))

    def test_raises_when_init_fails(self, mock_repo):
        mock_repo.init.side_effect = git_utils.git.exc.GitCommandError("git init", 255)

        with pytest.raises(VersionControlError):
            git_utils.init(Path())


class TestGetRepo:
    def test_returns_repo_object(self, mock_repo):
        repo = git_utils.get_repo(Path())

        assert isinstance(repo, mock_repo().__class__)

    def test_raises_version_control_error_when_no_git_repo_found(self, mock_repo):
        mock_repo.side_effect = git_utils.git.exc.InvalidGitRepositoryError

        with pytest.raises(VersionControlError):
            git_utils.get_repo(Path())


class TestCheckout:
    def test_git_lib_called_with_correct_command(self, mock_repo):
        git_utils.checkout(mock_repo, "master", force=True)

        mock_repo.git.checkout.assert_called_once_with("--force master")

    def test_raises_version_control_error_when_git_checkout_fails(self, mock_repo):
        mock_repo.git.checkout.side_effect = git_utils.git.exc.GitCommandError("git checkout", 255)

        with pytest.raises(VersionControlError):
            git_utils.checkout(mock_repo, "bad")
