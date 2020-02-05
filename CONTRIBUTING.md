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

## Merging the Pull Request

When merging the pull request we will normally squash merge the changes give it a title which provides context to
the changes:

- `<emoji> <Issue-Number> <Change Summary> (#<Pull Request Number>)`

An emoji is used to highlight what has occurred in the change. Commonly used emojis can be seen below, but for a full
list please see [Gitmoji](https://gitmoji.carloscuesta.me/):

Emoji | Topic(s)
------|---------
✨ | New features or enhancements.
🐛 | Bug / defect fixes.
🔒 | Fixing security issues.
⚡️ | Improving performance.
♻️ | Refactoring or addressing technical debt.
💥 | Breaking changes or removing functionality.
❗️ | Notice of deprecation.
📝 | Writing or updating documentation.
👷 | Adding to the CI or build system.
💚️ | Fixing CI or build system issues.
🚀 | Releasing or deploying.

For more on the version number scheme please see the [ReadMe](./README.md).

## One Last Thing...

For us to accept your code contributions, we will need you to agree to our 
[Mbed Contributor Agreement](https://os.mbed.com/contributor_agreement/) to give us the necessary rights to use and 
distribute your contributions.

Thank you :smiley:
