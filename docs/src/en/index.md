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

### Installing `bitwarden-import-msecure`

In the terminal (command prompt), execute:

```bash
pipx install bitwarden-import-msecure
```

## Usage

In mSecure, execute `File` → `Export` → `CSV...` and save the file.

In the terminal (command prompt) opened in the same folder as the exported file (or add the path to the folder):

```bash
bitwarden-import-msecure "mSecure Export File.csv"
```

It will create `bitwarden.json` in the same folder as the input file.

In Bitwarden, select `File` → `Import data` and choose File format: "Bitwarden (json)".
Choose the previously created file `bitwarden.json` and press "Import data".


### Advanced Usage

#### Output Formats

By default, the tool creates JSON format (recommended):

```bash
bitwarden-import-msecure "mSecure Export File.csv"
```

For CSV format (legacy, fewer features):

```bash
bitwarden-import-msecure "mSecure Export File.csv" --format csv
```

#### Custom Fields Handling

By default, extra mSecure fields become Bitwarden custom fields:

```bash
bitwarden-import-msecure "mSecure Export File.csv"
```

To add extra fields to notes instead:

```bash
bitwarden-import-msecure "mSecure Export File.csv" --extra-fields notes
```

#### Overwriting Files

If the output file already exists, use `--force`:

```bash
bitwarden-import-msecure "mSecure Export File.csv" --force
```

#### Patching Existing Exports

For users who previously imported with older versions (before 1.5.0) that missed some data:

1. Export your current Bitwarden data as JSON: `bitwarden_current.json`
2. Patch it with missing mSecure data:
   ```bash
   bitwarden-import-msecure "mSecure Export File.csv" bitwarden_current.json --patch
   ```
3. Remove all items from Bitwarden (backup first!)
4. Import the patched `bitwarden_current.json`

#### All Available Options

```bash
bitwarden-import-msecure --help
```

### What Gets Organized How

The tool automatically organizes your data:

- **Credit Cards**: Placed in "bank" folder
- **Items with "bank" in the name**: Also placed in "bank" folder
- **Tagged items**: Use mSecure tag as folder name
- **Login entries**: Become Bitwarden login items with URLs
- **Items without credentials/URLs**: Become secure notes
- **PIN fields**: Added as hidden custom fields

### Field Mapping

| mSecure Field | Bitwarden Equivalent |
|---------------|---------------------|
| Website | Login URI |
| Username | Login Username |
| Password | Login Password |
| Card Number | Card Number |
| Security Code | Card CVV |
| PIN | Hidden custom field |
| Other fields | Custom fields or notes |
