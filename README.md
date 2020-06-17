# Setup

1. Create colab notebook.
1. Mount Drive in files sidebar.
1. Make `work/env/config.py` on your Google Drive by analogy with `config_example.py`.

# Usage

Run the following code in your notebook:

    ```python
    !curl -LOs https://github.com/itesoro/colab_env/raw/master/setup.py 
    %run setup work/env/config.py
    ```
    
At the first run, script will generate ssh keys at `SSH_KEY_PATH` specified in `config.py`. Add public key to your github account.

To install python packages from private repository run the following line in your notebook:
```python
!pip install git+ssh://git@github.com/itesoro/<repository-name>.git
```
