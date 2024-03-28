# bitwarden-import-msecure

Migration from mSecure to Bitwarden.

Unlike the built-in Bitwarden import tool, this script does not place each secret into a separate folder. 
Instead, it organizes secrets into meaningful folders and offers several options to customize the import process.

Additionally, this simple Python script can be easily modified to meet your specific needs.

## Installation

### Installing pipx
[`pipx`](https://pypa.github.io/pipx/) creates isolated environments to avoid conflicts with existing system packages.

=== "MacOS"
    In the terminal, execute:
    ```bash
    brew install pipx
    pipx ensurepath
    ```

=== "Linux"
    First, ensure Python is installed.

    Enter in the terminal:
    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```

=== "Windows"
    First, install Python if it's not already installed.

    In the command prompt, type (if Python was installed from the Microsoft Store, use `python3` instead of `python`):
    ```bash
    python -m pip install --user pipx
    ```

### Installing `bitwarden-import-msecure`:
In the terminal (command prompt), execute:

```bash
pipx install bitwarden-import-msecure
```

## Usage

In mSecure execute `File` -> `Export` -> `CSV..` and save the file.

In the terminal (command prompt) opened in the same folder as the exported file (or add the path to the folder):

```bash
bitwarden-import-msecure "mSecure Export File.csv"
```

It will create `bitwarden.csv` in the same folder as input file.

In Bitwarden dialog `File` -> `Import data` select File format: "Bitwarden (csv)".
Choose previously create file `bitwarden.csv` and press "Import data".


### Advanced

Use 
```bash
bitwarden-import-msecure --help
```
to see all available options.