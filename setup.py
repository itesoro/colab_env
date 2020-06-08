WORK_DIR = '/content/drive/My Drive/work/tesoro'


def main():
    import os
    import json
    import getpass
    import shutil
    ENV_DIR = os.path.join(WORK_DIR, 'env')
    SSH_DIR = os.path.join(ENV_DIR, 'ssh')
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
    user_name = user['name']
    user_email = user['email']
    os.system(f'git config --global user.name "{user_name}"')
    os.system(f'git config --global user.email "{user_email}"')
    
    passphrase = None

    def enter_passphrase():
        nonlocal passphrase
        while True:
            passphrase = getpass.getpass(f'Enter passphrase for key "{KEY_PATH}": ')
            if len(passphrase) >= 5:
                return
            print('Passphrase is too short (minimum five characters)')

    enter_passphrase()
    while not os.path.isfile(KEY_PATH):
        if passphrase == getpass.getpass(f'Confirm passphrase: '):
            ret_code = os.system(f'ssh-keygen -t rsa -b 4096 -C "{user_email}" -f "{KEY_PATH}" -N {passphrase}')
            if ret_code == 0:
                print(f'Saved keys to "{SSH_DIR}"')
                break
        enter_passphrase()
    
    os.system('mkdir -p /root/.ssh')
    os.system(f'cp -f "{SSH_DIR}/id_rsa" /root/.ssh/id_rsa')
    os.system('ssh-keyscan github.com >> /root/.ssh/known_hosts')
    os.system('chmod 600 /root/.ssh/id_rsa')
    os.system('chmod 644 /root/.ssh/known_hosts')

    while True:
        ret_code = os.system(f'ssh-keygen -p -P "{passphrase}" -N "" -f /root/.ssh/id_rsa')
        if ret_code == 0:
            break
        enter_passphrase()
    if update_config:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)


main()
del main
