# Contribution Guide

Mbed OS is an open source project and we really appreciate your contributions to the tools. We are committed to
fostering a welcoming community, please see our Code of Conduct, which can be found here:

- [Code of Conduct](./CODE_OF_CONDUCT.md)

There are several ways to contribute:

- Raise an issue found via [GitHub Issues](https://github.com/ARMmbed/mbed-tools/issues).
- Open an [pull request](https://github.com/ARMmbed/mbed-tools/pulls) to:
  - Provide a fix.
  - Add an enhancement feature.
  - Correct, update or add documentation.
- Answering community questions on the [Mbed Forum](https://forums.mbed.com/).

## How to Contribute Documentation or Code

Please keep contributions small and independent. We would much rather have multiple pull requests for each thing done
rather than have them all in the same one. This will help us review, give feedback and merge in the changes. The
normal process to make a change is as follows:

1. Fork the repository.
2. Make your change and write unit tests, please try to match the existing documentation and coding style.
3. Add a news file describing the changes and add it in the `/news` directory, see the section _News Files_ below.
4. Write a [good commit message](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).
5. Push to your fork.
6. Submit a pull request.

We will review the proposed change as soon as we can and, if needed, give feedback. Please bear in mind that the tools
for Mbed OS are complex and cover a large number of use cases. This means we may ask for changes not only to ensure
that the proposed change meets our quality criteria, but also to make sure the that the change is generally useful and
doesn't impact other uses cases or maintainability.

### News Files

News files serve a different purpose to commit messages, which are generally written to inform developers of the
project. News files will form part of the release notes so should be written to target the consumer of the package or
tool.

- A news file should be added for each merge request to the directory `/news`.
- The text of the file should be a single line describing the change and/or impact to the user.
- The filename of the news file should take the form `<number>.<extension>`, e.g, `20191231.feature` where:
  - The number is either the issue number or, if no issue exists, the date in the form `YYYYMMDD`.
  - The extension should indicate the type of change as described in the following table:

| Change Type                                                                                                             | Extension  | Version Impact  |
|-------------------------------------------------------------------------------------------------------------------------|------------|-----------------|
| Backwards compatibility breakages or significant changes denoting a shift direction.                                    | `.major`   | Major increment |
| New features and enhancements (non breaking).                                                                           | `.feature` | Minor increment |
| Bug fixes or corrections (non breaking).                                                                                | `.bugfix`  | Patch increment |
| Documentation impacting the consumer of the package (not repo documentation, such as this file, for this use `.misc`).  | `.doc`     | N/A             |
| Deprecation of functionality or interfaces (not actual removal, for this use `.major`).                                 | `.removal` | None            |
| Changes to the repository that do not impact functionality e.g. build scripts change.                                   | `.misc`    | None            |

### Commit Hooks

We use [pre-commit](https://pre-commit.com/) to install and run commit hooks, mirroring the code checks we run in our CI
environment.

The `pre-commit` tool allows developers to easily install git hook scripts which will run on every `git commit`. The
`.pre-commit-config.yaml` in our repository sets up commit hooks to run pytest, black, mypy and flake8. Those checks
must pass in our CI before a PR is merged. Using commit hooks ensures you can't commit code which violates our style
and maintainability requirements.

To install the commit hooks for the repository (assuming you have activated your development environment as described in [the development guide](./DEVELOPMENT.md)), run:

```bash
$ pre-commit install
```
Our code checks will now run automatically every time you try to `git commit` to the repository.

If you prefer not to install the hook scripts, you can use
```bash
$ pre-commit run
```
to check your staged changes.

## Pull Requests and Commit Messages

We aim to compose and review patchsets, not individual patches.
When merging a pull request, we preserve the commit history. Ensure your commit history is clean and understandable.

We recommend the following commit structure in the following order:

1. Whitespace only changes
1. Style changes (although we use `black` to auto format the code so these should be rare)
1. Refactoring (no functional change)
1. Meaningful behavioural changes

Follow [this guide](https://chris.beams.io/posts/git-commit/) to ensure you're writing good commit messages.

## Creating a Release

To create a production release of mbed-tools, perform the following steps:

1. Check out the `master` branch; ensure it is clean and up to date.
1. Run `tox -e preprelease`, this will update the necessary files, create a commit and tag it with the new release version number.
1. Push the commit to `master`.
1. Push the tag.

The CI will detect a new tag has been created and run the "Build and Deploy" pipeline, which then pushes the release to pyPI.

> **_NOTE:_**  The release process relies on a shell script `ci_scripts/prep-release`, so will not work on Windows systems.

## Contribution Agreement

For us to accept your code contributions, we will need you to agree to our
[Mbed Contributor Agreement](https://os.mbed.com/contributor_agreement/) to give us the necessary rights to use and
distribute your contributions.

Thank you for contributing to `mbed-tools`.
