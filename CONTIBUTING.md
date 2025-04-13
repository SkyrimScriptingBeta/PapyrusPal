# CONTRIBUTING (Developer Guide)

## Prerequisites

- Python 3.13
  - _Recommend using `pyenv` to manage your Python installation:_  
    https://github.com/pyenv-win/pyenv-win
- Poetry 2.0+
  - _Install Poetry:_  
    https://python-poetry.org/docs/#installation
    
## Setup your environment

> _Optional but popular preference:_  
> `poetry config virtualenvs.in-project true`
>
> This will tell `poetry` to create a `.venv` folder in the root of the project
> instead of a global virtual environment.
>
> You must run this before `poetry install` to take effect.

### Install dependencies

- `poetry install`
