# Usage

1. Create colab notebook.
2. Mount Drive in files sidebar.
3. Run the following cell:
    ```python
    !curl -LOs https://github.com/itesoro/colab_env/raw/master/setup.py 
    %run setup work/env/config.py
    ```
    
If running the first time add public key to your github account.

To install python packages from private repository run the following line in your notebook
```python
!pip install git+ssh://git@github.com/itesoro/<repository-name>.git
```
