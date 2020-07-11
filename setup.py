from IPython.core.magic import register_line_magic


def main():
    import os
    import sys
    import getpass
    import shutil
    from IPython.display import clear_output
    
    def link(path):
        new_path = f'/content/{os.path.basename(path)}'
        if os.path.islink(new_path):
            return new_path
        if os.system(f'ln -s "{path}" "{new_path}"') == 0:
            return new_path
        return path

    sys.argv = sys.argv[1:]
    MY_DRIVE_DIR = f'/content/drive/My Drive'
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
def pip_install_editable(args):
    import os, sys
    args = args.split()
    url = args[0]
    branch = None
    for i in range(1, len(args) - 1):
        if args[i] == '-b' or args[i] == '--branch':
            branch = args[i + 1]
    name, git_ext = os.path.splitext(os.path.basename(url))
    assert git_ext == '.git'
    path = os.path.abspath(name)
    if os.path.isdir(path):
        return
    ok = True

    def shell(cmd):
        nonlocal ok
        if not ok:
            return
        ret_code = os.system(cmd)
        if ret_code != 0:
            print(f'{cmd} returned {ret_code}', file=sys.stderr)
            ok = False

    shell(f'git clone "{url}" "{path}"')
    if branch:
        shell(f'cd "{path}" && git checkout {branch}')
    shell(f'pip install -e "{path}"')
    if ok:
        sys.path.append(path)
        print(f'Successfully installed {name}')
    else:
        os.system(f'rm -rf "{path}"')
        print(f"Can't install {name}", file=sys.stderr)


main()
del main, pip_install_editable, register_line_magic
