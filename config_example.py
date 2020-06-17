import os

export = ['WORK_DIR', 'USER_NAME', 'USER_EMAIL']

USER_NAME = 'First Name'
USER_EMAIL = 'first_name@gmail.com'
WORK_DIR = link(f'{MY_DRIVE_DIR}/work')  # create symlink `/content/work` pointing to `My Drive/work`.
SSH_KEY_PATH = f'{WORK_DIR}/env/ssh/id_rsa'
