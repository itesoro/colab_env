WORK_DIR = '/content/drive/My Drive/work/tesoro'


def main():
    import os
    import json
    import getpass
    import shutil
    ENV_DIR = os.path.join(WORK_DIR, 'env')
    SSH_DIR = os.path.join(ENV_DIR, '.ssh')
    CONFIG_PATH = os.path.join(ENV_DIR, 'config.json')
    KEY_PATH = os.path.join(SSH_DIR, 'id_rsa')
    os.makedirs(SSH_DIR, exist_ok=True)
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        update_config = False
    except Exception:
        config = {}
        update_config = True
    user = config.get('user')
    if user is None:
        user = {
            'name': input('Enter your full name: '),
            'email': input('Enter your email: ')
        }
        config['user'] = user
        update_config = True
    
    passphrase = None

    def enter_passphrase():
        nonlocal passphrase
        passphrase = getpass.getpass(f'Enter passphrase for key "{KEY_PATH}": ')

    enter_passphrase()
    if not os.path.isfile(KEY_PATH):
        email = user['email']
        while True:
            ret_code = os.system(f'ssh-keygen -t rsa -b 4096 -C "{email}" -f "{KEY_PATH}" -N {passphrase}')
            if ret_code == 0:
                break
            assert ret_code == 256, f'{ret_code}'
            print(f'Saving key "{KEY_PATH}" failed: passphrase is too short (minimum five characters)')
            enter_passphrase()
    
    os.system(f'\cp -rf "{SSH_DIR}" /root')
    while True:
        ret_code = os.system(f'ssh-keygen -q -p -P "{passphrase}" -N "" -f /root/.ssh/id_rsa')
        if ret_code == 0:
            break
        enter_passphrase()
    if update_config:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)


main()
del main
