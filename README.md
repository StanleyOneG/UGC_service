## Установка poetry и запуск виртауального окружения
Для Linux, macOS, Windows (WSL):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Для Windows (Powershell):
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
В macOS и Windows сценарий установки предложит добавить папку с исполняемым файлом poetry в переменную PATH. Сделайте это, выполнив следующую команду:

macOS
```bash
export PATH=$PATH:$HOME/.local/bin
```
Windows
```bash
$Env:Path += ";C:\Users\jetbrains\AppData\Roaming\Python\Scripts"; setx PATH "$Env:Path"
```
Не забудьте поменять jetbrains на имя вашего пользователя. Настройка окружения poetry для pycharm [тут](https://www.jetbrains.com/help/pycharm/poetry.html)

Для проверки установки выполните следующую команду:
```bash
poetry --version
```
Установка автодополнений bash(опцонально)
```bash
poetry completions bash >> ~/.bash_completion
```

Изменить конфигурацию Poetry (опционально).

```shell
poetry config virtualenvs.in-project true
```
> **Note**:
> Позволяет создавать виртуальное окружение в папке проекта.

### Установка

1. Клонировать репозиторий.

    ```shell
    git clone https://github.com/StanleyOneG/ugc_sprint_1.git
    cd ugc_sprint_1
    ```

2. Создать и активировать виртуальное окружение.

    > **Warning**:
    > Необходимы для дальнейшей разработки приложения.

    ```shell
    poetry install
    poetry shell
    ```

3. Настроить pre-commit.

    ```shell
    pre-commit install --all
    ```
    > **Note**:
    > Перед каждым коммитом будет запущен линтер и форматтер,
    > который автоматически отформатирует код
    > согласно принятому в команде codestyle.

    > **Note**:
    > Если в процессе коммита линтер отформатирует код, коммит создан не будет,
    > а отформатированный файл отобразится в статусе *modified*.
    > В этом случае, необходимо добавить файл в *staged*
    > ```git add .```
    > и повторить коммит.

    > **Note**:
    > Если не видно какая ошибка мешает выполнить commit, то можно запустить хуки в ручную можно командой
    > ```bash
    > pre-commit run --all-files
    > ```

4. В дальнейшем для установки библиотек пользоваться командой:

    > ```bash
    > poetry add <libname>
    > ```
