import getpass

x = getpass.getpass('Enter password: ')
print('Test', x)

from setuptools import setup, find_packages

setup(
    name='colab_env',
    version='1.0.0',
    url='https://github.com/itesoro/colab_env',
    packages=find_packages()
)
