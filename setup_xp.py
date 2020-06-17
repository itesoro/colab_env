from IPython.core.magic import register_line_magic


def main():
    import os
    import sys
    import getpass
    import shutil
    from IPython.display import clear_output

    DRIVE_DIR = '/content/drive'
    HIDDEN_DRIVE_DIR = '/content/.drive'

    def hide_drive_mount_point():
        nonlocal DRIVE_DIR, HIDDEN_DRIVE_DIR
        if DRIVE_DIR == HIDDEN_DRIVE_DIR:
            return
        ok = True
        if not os.path.isdir(HIDDEN_DRIVE_DIR):
            ok = ok and os.system(f'mkdir -p "{HIDDEN_DRIVE_DIR}"') == 0
            ok = ok and os.system(f'mount --move "{DRIVE_DIR}" "{HIDDEN_DRIVE_DIR}"') == 0
            if ok:
                ok = os.system(f'rmdir "{DRIVE_DIR}"') == 0
            else:
                ok = os.system(f'rmdir "{HIDDEN_DRIVE_DIR}"') == 0
        if ok:
            DRIVE_DIR = HIDDEN_DRIVE_DIR
    
    def link(path):
        new_path = f'/content/{os.path.basename(path)}'
        if os.path.islink(new_path):
            return new_path
        if os.system(f'ln -s "{path}" "{new_path}"') == 0:
            return new_path
        return path

    hide_drive_mount_point()
    sys.argv = sys.argv[1:]
    MY_DRIVE_DIR = f'{DRIVE_DIR}/My Drive'
    config = {'MY_DRIVE_DIR': MY_DRIVE_DIR, 'link': link}
    config_path = os.path.join(MY_DRIVE_DIR, sys.argv[0])
    exec(open(config_path).read(), config)
    USER_NAME = config['USER_NAME']
    USER_EMAIL = config['USER_EMAIL']
    KEY_PATH = config['SSH_KEY_PATH']
    DST_KEY_PATH = '/root/.ssh/id_rsa'
    SSH_DIR = os.path.dirname(KEY_PATH)
    DST_SSH_DIR = os.path.dirname(DST_KEY_PATH)
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
                    clear_output = lambda: None
                    break
            enter_passphrase()
        
        os.system(f'mkdir -p "{DST_SSH_DIR}"')
        os.system(f'cp -f "{SSH_DIR}/id_rsa" "{DST_KEY_PATH}"')
        os.system(f'chmod 600 "{DST_KEY_PATH}"')
        os.system(f'ssh-keyscan github.com >> "{DST_SSH_DIR}/known_hosts"')
        os.system(f'chmod 644 "{DST_SSH_DIR}/known_hosts"')

        while True:
            ret_code = os.system(f'ssh-keygen -p -P "{passphrase}" -N "" -f "{DST_KEY_PATH}"')
            if ret_code == 0:
                break
            enter_passphrase()

    globals_ = globals()
    for k in config.get('export', []):
        globals_[k] = config[k]
    clear_output()


@register_line_magic
def pip_install_editable(url):
    import os, sys
    name, git_ext = os.path.splitext(os.path.basename(url))
    assert git_ext == '.git'
    path = os.path.abspath(name)
    if not os.path.isdir(path):
        ok = True
        ok = ok and (os.system(f'git clone "{url}" "{path}"') == 0)
        ok = ok and (os.system(f'pip install -e "{path}"') == 0)
        if ok:
            sys.path.append(path)
            print(f'Successfully installed {name}')
        else:
            print(f"Can't install {name}")


main()
del main, pip_install_editable, register_line_magic
