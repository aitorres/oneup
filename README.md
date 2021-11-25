# OneUp

A CLI tool to check for dependency updates for Python, in Python.

## What's this?

`oneup` is a simple command-line interface to aid developers in determining the most recent version of their project's dependencies, as specified in files such as `requirements.txt` and `pyproject.toml`.

Right now, the tool can parse your dependency lists and report the latest version of all your dependencies to the standard output. In the future, the tool might add some other features such as: automatically updating your lists with a latest version, if desired, and only showing the latest version of dependencies if they differ from your currently specified version (or range).

## Installation

You can use your Python package manager (e.g. [pip](https://pip.pypa.io/en/stable/)) to install `oneup`.

```bash
pip install oneup
```

## Usage

`oneup` comes with a command-line interface and will automatically detect any supported dependency files in the current directory:

```bash
oneup
```

You can also specify which file to check:

```bash
oneup --file path/to/requirements.txt
```

A complete list of arguments and flags can be found by running:

```bash
oneup --help
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate; a minimum coverage of 75% is expected (and enforced by Github Actions!).

## License

This project is licensed under the [GNU Affero General Public License v3.0](https://github.com/aitorres/oneup/blob/main/LICENSE).
