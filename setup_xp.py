def main():
    import os
    import sys
    import getpass
    import shutil
    sys.argv = sys.argv[1:]
    MY_DRIVE_DIR = '/content/drive/My Drive'
    config = {'MY_DRIVE_DIR': MY_DRIVE_DIR}
    config_path = os.path.join(MY_DRIVE_DIR, sys.argv[0])
    exec(open(config_path).read(), config)
    USER_NAME = config['USER_NAME']
    USER_EMAIL = config['USER_EMAIL']
    KEY_PATH = config['SSH_KEY_PATH']
    DST_KEY_PATH = '/root/.ssh/id_rsa'
    SSH_DIR = os.path.dirname(KEY_PATH)
    os.system(f'git config --global user.name "{USER_NAME}"')
    os.system(f'git config --global user.email "{USER_EMAIL}"')
    
    passphrase = None

    def enter_passphrase():
        nonlocal passphrase
        while True:
            passphrase = getpass.getpass(f'Enter passphrase for key "{KEY_PATH}": ')
            if len(passphrase) >= 5:
                return
            print('Passphrase is too short (minimum five characters)')

    if not os.path.isfile(DST_KEY_PATH):
        enter_passphrase()
        while not os.path.isfile(KEY_PATH):
            os.makedirs(SSH_DIR, exist_ok=True)
            if passphrase == getpass.getpass(f'Confirm passphrase: '):
                ret_code = os.system(f'ssh-keygen -t rsa -b 4096 -C "{USER_EMAIL}" -f "{KEY_PATH}" -N {passphrase}')
                if ret_code == 0:
                    print(f'Saved keys to "{SSH_DIR}"')
                    break
            enter_passphrase()
        
        os.system('mkdir -p /root/.ssh')
        os.system(f'cp -f "{SSH_DIR}/id_rsa" "{DST_KEY_PATH}"')
        os.system('ssh-keyscan github.com >> /root/.ssh/known_hosts')
        os.system('chmod 600 /root/.ssh/id_rsa')
        os.system('chmod 644 /root/.ssh/known_hosts')

        while True:
            ret_code = os.system(f'ssh-keygen -p -P "{passphrase}" -N "" -f "{DST_KEY_PATH}"')
            if ret_code == 0:
                break
            enter_passphrase()

    globals_ = globals()
    for k in config.get('export', []):
        globals_[k] = config[k]

main()
del main
