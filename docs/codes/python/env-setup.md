---
title: Env setup
---

# Python environment setup

Setup the backbone of every project.

## Pre-req

Is Python already installed in the system?

=== "macOS / Linux"

    ```bash
    python3 --version
    ```

=== "Windows"

    ```powershell
    python --version
    ```

## venv

Built-in method to create env, use base version of `python3` in the system

=== "macOS / Linux"

    ```bash
    # python -m venv <folder path>
    python3 -m venv venv
    source venv/bin/activate

    pip install -r requirements.txt
    ```

=== "Windows"

    ```powershell
    python -m venv venv

    .\venv\Scripts\Activate.ps1

    pip install -r requirements.txt
    ```

## uv

Better than `poetry` at speed, while using for static dependencies lock

Doc: [Here](https://docs.astral.sh/uv/)

### Obtaining `uv`

=== "macOS / Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    OR throught `pip` on base env:

    ```bash
    pip install uv
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    OR throught `pip` on base env:

    ```bash
    pip install uv
    ```

### Setup project

[`uv` features](https://docs.astral.sh/uv/getting-started/features/)


```bash
# Init project
# uv init <project/folder-name>
uv init myproject

# Add library
uv add fastapi

# Lock dependencies with uv.lock file
uv lock

# Install depenencies from uv lock
uv sync
```


## (Mini)conda

Environment creation with a pinned Python version.

Requires (Mini)conda installation to work.

Get here: [Anaconda](https://www.anaconda.com/docs/getting-started/installation)

=== "macOS / Linux"

    ```bash
    # conda create --name <env-name> python=3.12
    conda create --name venv python=3.12

    # Add initial packages
    conda create --name venv python=3.12 fastapi uvicorn asyncpg

    conda activate venv

    pip install -r requirements.txt
    ```

=== "Windows"

    ```powershell
    # conda create --name <env-name> python=3.12
    conda create --name venv python=3.12

    # Add initial packages
    conda create --name venv python=3.12 fastapi uvicorn asyncpg

    conda activate venv

    pip install -r requirements.txt
    ```



## Related

- [Project scaffold](project-scaffold.md) — what to put in the project once the
  environment exists
