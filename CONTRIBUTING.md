# Contribution Guide

Mbed OS is an open source project and we really appreciate your contributions
to the tools. We are committed to fostering a welcoming community, please see
our Code of Conduct, which can be found here:

- [Code of Conduct](./CODE_OF_CONDUCT.md)

There are several ways to contribute:

- Raise an issue found via [GitHub
  Issues](https://github.com/ARMmbed/mbed-tools/issues).
- Open an [pull request](https://github.com/ARMmbed/mbed-tools/pulls) to:
  - Provide a fix.
  - Add an enhancement feature.
  - Correct, update or add documentation.
- Answering community questions on the [Mbed Forum](https://forums.mbed.com/).

## How to Contribute Documentation or Code

Please keep contributions small and independent. We would much rather have
multiple pull requests for each thing done rather than have them all in the
same one. This will help us review, give feedback and merge in the changes. The
normal process to make a change is as follows:

1. Fork the repository.
2. Make your change and write unit tests, please try to match the existing
   documentation and coding style.
3. Add a news file describing the changes and add it in the `/news` directory,
   see the section _News Files_ below.
4. Write a [good commit
   message](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).
5. Push to your fork.
6. Submit a pull request.

We will review the proposed change as soon as we can and, if needed, give
feedback. Please bear in mind that the tools for Mbed OS are complex and cover
a large number of use cases. This means we may ask for changes not only to
ensure that the proposed change meets our quality criteria, but also to make
sure the that the change is generally useful and doesn't impact other uses
cases or harm maintainability.

If you are new to developing on Python projects, you may find [our development
tutorial](#Development-and-Testing) valuable. We cover how to get a Python
development environment set up, how to use tox, and other tips.

### News Files

News files serve a different purpose to commit messages, which are generally
written to inform developers of the project. News files will form part of the
release notes so should be written to target the consumer of the package or
tool.

- A news file should be added for each merge request to the directory `/news`.
- The text of the file should be a single line describing the change and/or
  impact to the user.
- The filename of the news file should take the form `<number>.<extension>`,
  e.g, `20191231.feature` where:
  - The number is either the issue number or, if no issue exists, the date in
    the form `YYYYMMDD`.
  - The extension should indicate the type of change as described in the
    following table:

| Change Type                                                                                                             | Extension  | Version Impact  |
|-------------------------------------------------------------------------------------------------------------------------|------------|-----------------|
| Backwards compatibility breakages or significant changes denoting a shift direction.                                    | `.major`   | Major increment |
| New features and enhancements (non breaking).                                                                           | `.feature` | Minor increment |
| Bug fixes or corrections (non breaking).                                                                                | `.bugfix`  | Patch increment |
| Documentation impacting the consumer of the package (not repo documentation, such as this file, for this use `.misc`).  | `.doc`     | N/A             |
| Deprecation of functionality or interfaces (not actual removal, for this use `.major`).                                 | `.removal` | None            |
| Changes to the repository that do not impact functionality e.g. build scripts change.                                   | `.misc`    | None            |

### Commit Hooks

We use [pre-commit](https://pre-commit.com/) to install and run commit hooks,
mirroring the code checks we run in our CI environment.

The `pre-commit` tool allows developers to easily install git hook scripts
which will run on every `git commit`. The `.pre-commit-config.yaml` in our
repository sets up commit hooks to run pytest, black, mypy and flake8. Those
checks must pass in our CI before a PR is merged. Using commit hooks ensures
you can't commit code which violates our style and maintainability
requirements.

To install the commit hooks for the repository (assuming you have activated
your development environment as described in [the development
guide](./DEVELOPMENT.md)), run:

```bash
$ pre-commit install
```
Our code checks will now run automatically every time you try to `git commit`
to the repository.

If you prefer not to install the hook scripts, you can use
```bash
$ pre-commit run
```
to check your staged changes.

## Pull Requests and Commit Messages

We aim to compose and review patchsets, not individual patches. When merging a
pull request, we preserve the commit history. Ensure your commit history is
clean and understandable.

We recommend the following commit structure in the following order:

1. Whitespace only changes
1. Style changes (although we use `black` to auto format the code so these
   should be rare)
1. Refactoring (no functional change)
1. Meaningful behavioural changes

We also recommend adding a prefix to your commit message to highlight the area
of relevance. Write prefixes in lowercase, followed by a colon, followed by a
space, and then finally the commit title. Some example prefixes include the
following:

- `project: `
- `config: `
- `tests: `
- `docs: `
- `cli: `
- `travis: `
- `ci: `

Follow [Chris Beams' article on how to write a Git commit
message](https://chris.beams.io/posts/git-commit/) to ensure you're writing
good commit messages.

### An example commit message

```
commit 23efe7ba1009a0b0db890df3b940157c732085b7
Author: Vikas Katariya <Vikas.katariya@arm.com>
Date:   Thu Nov 26 11:36:02 2020 +0000

deploy: Use default branch from remote repository

Make sure we checkout the default branch from the remote repository, if
there is no git hash present in the .lib file.

We also need to fetch the git repository before performing a checkout
when using the `deploy` command. This makes sure we have the latest
changes in the upstream repo.

Fixes #122

```

## Contribution Agreement

Mbed previously required a signed contributor agreement in order to accept
contributions. Mbed no longer requires such an agreement. Mbed projects (unless
otherwise noted in the specific project) now accept contributions under
Apache-2.0 directly. For more details, refer to [the Mbed OS contributing
guide](https://os.mbed.com/docs/mbed-os/latest/contributing/index.html)

Thank you for contributing to `mbed-tools`.

# Development and Testing

For development and testing purposes, it is essential to use a virtual
environment. tox is a commonly used development tool that helps manage virtual
environments.

## Setup Python and tox

`mbed-tools` is compatible with Python 3.6 or later.

If you are on a Linux distribution, or macOS, you will find that Python comes
pre-installed on your system. **Do not use the pre-installed versions of Python
for development.**

Below are links to guides for correctly setting up a development ready version
of Python 3 on common platforms:

* [macOS](https://docs.python-guide.org/starting/install3/osx/#doing-it-right)
* [Ubuntu](https://docs.python-guide.org/starting/install3/linux/)
* [Windows](https://docs.python-guide.org/starting/install3/win/)

On Windows we have also found the [Python Launcher for
Windows](https://docs.python.org/3/using/windows.html) to be a reasonable
alternative.

After you have set up your Python 3 installation, install tox (the `--user`
flag is important **never use `sudo` to install Python packages!**)

On macOS, with [the defacto macOS package manager, Homebrew](https://brew.sh/):

```bash
brew install tox
```

On other platforms, use your native package manager's tox package or your
Python environment's Python package manager, pip, like so:

```bash
python3 -m pip install --user tox
```

Check that tox is in the binary path

```bash
tox --version
```

If not, find the user base binary directory

```bash
python -m site --user-base
#~ /Users/<username>/Library/Python/3.9
```

Append `bin` to the directory returned and add this to your path by updating
`~/.profile`. For example you might add the following:

```bash
export PATH=~/Library/Python/3.9/bin/:$PATH
```

## Setup Development Environment

Clone the `mbed-tools` GitHub repository.

```bash
git clone git@github.com:ARMmbed/mbed-tools.git
```

Set up the development environment using tox (tox will create a development
environment at mbed-tools/.venv):

```bash
cd mbed-tools/
tox -e dev
source .venv/bin/activate
```

## Unit Tests, Code Formatting and Static Analysis

After you have activated your development environment, run `tox -e
linting,py39` to run unit tests and static code analysis checks:

```bash
tox -e linting,py39
```

This will run `black`, `flake8`, `mypy` and `pytest`. If you would like to run
these tools individually, see below:

Run unit tests:

```bash
pytest
```

Run code formatter (it will format files in place):

```bash
black .
```

Run static analysis (note that no output means all is well):

```bash
flake8
```

Perform static type check:

```bash
mypy src/mbed_tools
```

## Type hints

Type hints should be used in the code wherever possible. Since the
documentation shows the function signatures with the type hints
there is no need to include additional type information in the docstrings.

## Code Climate

Code Climate is integrated with our GitHub flow. Raising a pull request that
fails any of the configured rules will prevent your pull request from being
merged.

If you prefer to view the Code Climate report on your machine, prior to sending
a pull request, you can use the [cli provided by Code
Climate](https://docs.codeclimate.com/docs/command-line-interface).

Plugins for various tools are also available:
  - [Atom](https://docs.codeclimate.com/docs/code-climate-atom-package)
  - [PyCharm](https://plugins.jetbrains.com/plugin/13306-code-cleaner-with-code-climate-cli)
  - [Vim](https://docs.codeclimate.com/docs/vim-plugin)

## Documenting code

Inclusion of docstrings is needed in all areas of the code for Flake8 checks in
the CI to pass.

We use
[google-style](http://google.github.io/styleguide/pyguide.html#381-docstrings)
docstrings.

To set up google-style docstring prompts in Pycharm:

* in the menu navigate to Preferences > Tools > Python Integrated Tools
* in the dropdown for docstring format select 'Google'

For longer explanations, you can also include markdown. Markdown can also be
kept in separate files in the `docs/user_docs` folder and included in a
docstring in the relevant place using the [reST
include](https://docutils.sourceforge.io/docs/ref/rst/directives.html#including-an-external-document-fragment)
as follows:

```python
    .. include:: ../docs/user_docs/documentation.md
```

### Building docs locally

You can do a preview build of the documentation locally by running:

```bash
generate-docs
```

This will generate the docs and output them to `local_docs`. This should only
be a preview. Since documentation is automatically generated by the CI you
shouldn't commit any docs html files manually. The docs will be generated and
checked in as part of the release process.

### Viewing docs generated by the CI

If you want to preview the docs generated by the CI you can view them in the
Azure pipeline artifacts directory for the build.

Documentation only gets committed back to this repo to the `docs` directory
during a release and this is what gets published to Github pages. Don't modify
any of the files in this directory by hand.

## Creating a Release

Production releases of mbed-tools are created automatically every night by our
continuous delivery system (implemented in Azure Pipelines). There should be no
human intervention required to deploy mbed-tools to pypi.

If you wish to create a production release of mbed-tools without waiting for
the continuous deployment system to create one, you can perform the following
steps:

1. Check out the `master` branch; ensure it is clean and up to date.
1. Run `tox -e preprelease`, this will update the necessary files, create a
   commit and tag it with the new release version number.
1. Push the commit to `master`.
1. Push the tag.

The CI will detect a new tag has been created and run the "Build and Deploy"
pipeline, which then pushes the release to pyPI.

> **_NOTE:_**  The release process relies on a shell script
> `ci_scripts/prep-release`, so will not work on Windows systems.
