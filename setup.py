import os
import getpass

os.system(f'ssh-keygen -p -P "{getpass.getpass("Enter passphrase: ")}" -N "" -f /root/.ssh/id_rsa')

WDIR = '/content/drive/My Drive/work/tesoro'
