# bitwarden-import-msecure

Переход с mSecure на Bitwarden

## Установка

## Установка pipx
[`pipx`](https://pypa.github.io/pipx/) создает изолированные среды, чтобы избежать конфликтов с 
существующими системными пакетами.

=== "MacOS"
    В терминале выполните:

    ```bash
    brew install pipx
    pipx ensurepath
    ```

=== "Linux"
    Сначала убедитесь, что Python установлен.

    Введите в терминал:

    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```

=== "Windows"
    Сначала установите Python, если он еще не установлен.

    В командной строке введите (если Python был установлен из Microsoft Store, используйте `python3` вместо `python`):
    
    ```bash
    python -m pip install --user pipx
    ```

## Установка `bitwarden-import-msecure`:
В терминале (командной строке) выполните:

```bash
pipx install bitwarden-import-msecure
```

## Использование

В mSecure выберите `File` -> `Export` -> `CSV..` и сохраните файл.

Преобразуйте файл в формат Bitwarden:

```bash
bitwarden-import-msecure "mSecure Export File.csv"
```

Это создаст `bitwarden.csv` в той же папке, что и исходный файл.

В диалоговом окне Bitwarden выберите `Файл` -> `Импорт данных`, выберите Формат файла: "Bitwarden (csv)".
Выберите ранее созданный файл `bitwarden.csv` и нажмите "Импорт данных".
