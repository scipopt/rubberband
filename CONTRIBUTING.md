# Contributing

This project adheres to the [Contributor Covenant Code of Conduct][code-of-conduct]. By participating, you are expected to honor this code.
[code-of-conduct]: http://contributor-covenant.org/version/1/4/

## Getting started

The best way to start developing this project is to set up a virtualenv and install the requirements. This can also be done with [conda](http://conda.pydata.org/docs/).

    git clone <my remote url/rubberband.git>
    cd rubberband
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

Run tests to confirm that everything is set up properly.

    pip install -e .
	py.test tests/

## Submitting a pull request

1. Fork this repository
2. Create a branch: `git checkout -b my_feature`
3. Make changes
4. Install and run `flake8 rubberband/`to ensure that your changes conform to the coding style of this project
5. Commit: `git commit -am "Great new feature that closes #3"`. Reference any related issues in the first line of the commit message.
6. Push: `git push origin my_feature`
7. Open a pull request
8. Pat yourself on the back for making an open source contribution :)

## Other considerations

- Please review the open issues before opening a PR.
- Significant changes or new features should be documented in [`README.md`](README.md).
- Writing tests is never a bad idea. Make sure all tests are passing before opening a PR.

