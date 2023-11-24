from IPython.core.magic import register_line_magic


def setup_ssh_agent():
    import os, re, subprocess
    env_vars = ['SSH_AUTH_SOCK', 'SSH_AGENT_PID']
    if env_vars[0] in os.environ:
        return
    process = subprocess.run(['ssh-agent', '-s'], stdout=subprocess.PIPE, text=True)
    pattern = ''.join(map(lambda k: f'.*^\s*{k}=(?P<{k}>[^;]+)', env_vars))
    m = re.search(pattern, process.stdout, re.MULTILINE | re.DOTALL)
    if m is None:
        raise RuntimeError(f"Can't parse output of `ssh-agent -s`: {process.stdout}")
    os.environ.update(m.groupdict())


def main():
    import os, sys, getpass, shutil, pexpect
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
    if not os.path.isfile(DST_KEY_PATH + '.pub'):
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

        setup_ssh_agent()
        child = pexpect.spawn(f'ssh-add {DST_KEY_PATH}')
        while True:
            index = child.expect(['Enter passphrase for .*:', 'Bad passphrase, try again for .*:', pexpect.EOF, pexpect.TIMEOUT])
            if index > 1:
                if index == 2:
                    with open(DST_KEY_PATH + '.pub', 'wb') as f:
                        pass
                break
            if passphrase is None:
                enter_passphrase()
            child.sendline(passphrase)
            passphrase = None

    globals_ = globals()
    for k in config.get('export', []):
        globals_[k] = config[k]
    import nest_asyncio
    nest_asyncio.apply()
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
        shell(f'cd "{path}" && (git checkout {branch} || git checkout -b {branch})')
    shell(f'pip install -e "{path}"')
    if ok:
        sys.path.append(path)
        print(f'Successfully installed {name}')
    else:
        os.system(f'rm -rf "{path}"')
        print(f"Can't install {name}", file=sys.stderr)


class ignore_import_errors:
    """
    A context manager to suppress import errors for specified packages.

    Replaces failed imports from the specified packages with dummy objects,
    allowing the program to continue running.

    Parameters
    ----------
    packages : iterable
        Names of packages for which import errors are to be ignored.

    Examples
    --------
    >>> with ignore_import_errors(packages=('nonexistent_module', 'another_nonexistent')):
    ...     import nonexistent_module
    ...     from another_nonexistent import some_function
    ...     # ImportErrors for the specified modules are ignored.
    ...     # The code within the block continues to execute.

    Notes
    -----
    Use this context manager to handle optional dependencies or to gracefully
    degrade functionality when certain imports are unavailable.
    """

    def __init__(self, *, packages):
        import builtins
        self.__builtins = builtins
        self.packages = set(packages)

    def __enter__(self):
        self.__real_import = self.__builtins.__import__
        self.__builtins.__import__ = self.__import

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__builtins.__import__ = self.__real_import

    def __import(self, name, globals={}, locals={}, fromlist=[], level=0):
        try:
            return self.__real_import(name, globals, locals, fromlist, level)
        except Exception:
            if not name.split('.')[0] in self.packages:
                raise
        return self._DummyObject()

    class _DummyObject:
        _instance = None

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(ignore_import_errors._DummyObject, cls).__new__(cls)
            return cls._instance

        def __getattr__(self, name):
            return self


main()
del main, pip_install_editable, register_line_magic, setup_ssh_agent
