## Pull Request template
Please go through these steps before you submit a PR.

1. Make sure that you've opened an issue describing the problem you want to fix or the feature you want to add.
2. Make sure that your PR is not a duplicate.
3. If not, then make sure that:

    a. You have a descriptive commit message with a short title (first line).

    b. You have only one commit (if not, squash them into one commit).

    c. `docker compose up` doesn't show any errors. If it does, fix them first and amend your commit (`git commit --amend`).

4. **After** these steps, you're ready to open a pull request.

    a. Your pull request MUST NOT target the `master` branch on this repository. You probably want to target `dev` instead.

    b. Give a descriptive title to your PR.

    c. Provide a description of your changes.

    d. Put `closes #XXXX` in your comment to auto-close the issue that your PR fixes (if such).

IMPORTANT: Please review the [CONTRIBUTING.md](../../CONTRIBUTING.md) file for detailed contributing guidelines.

**PLEASE REMOVE THIS TEMPLATE BEFORE SUBMITTING**
