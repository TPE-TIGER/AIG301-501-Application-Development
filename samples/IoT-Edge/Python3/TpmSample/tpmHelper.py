import os, subprocess

class tpmHelper():
    primary_obj = 'primary.tmp'
    child_obj = 'child.tmp'
    child_pub = 'child.pub'
    child_priv = 'child.priv'

    def __init__(self):
        print('Creating Primary Key...')
        p = subprocess.Popen('tpm2_createprimary -c ' + self.primary_obj, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        self.load()

    def load(self):
        if not os.path.exists(self.child_pub) or not os.path.exists(self.child_priv):
            print('Creating Child Object...')
            p = subprocess.Popen('tpm2_create -u ' + self.child_pub + ' -r '+ self.child_priv + ' -C ' + self.primary_obj, \
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.communicate()

        print('Loading Child Object into TPM...')
        p = subprocess.Popen('tpm2_load -u ' + self.child_pub + ' -r ' + self.child_priv + ' -C ' + self.primary_obj + ' -c ' + self.child_obj, \
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            print('Error: Failed to load child object, abandoning existing child object...')
            try:
                os.remove(self.child_pub)
                os.remove(self.child_priv)
            except:
                pass
            self.load()

    def __del__(self):
        try:
            os.remove(self.primary_obj)
            os.remove(self.child_obj)
        except:
            pass

    def encrypt(self, output_str, input_str, is_plain_file=False, is_cipher_file=False):
        command = 'tpm2_rsaencrypt -c ' + self.child_obj

        if is_plain_file:
            if not os.path.exists(input_str):
                print("Error: Input file doesn't exist, path = " + input_str)
                return None
            command = command + ' ' + input_str
        else:
            command = 'echo -n \'' + input_str + '\' | ' + command

        if is_cipher_file:
            command = command + ' -o ' + output_str
        else:
            command = command + ' | base64 -w 0'

        print('Encrypting...')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            print('Error[{0}]: Encryption failed, out = {1}, error = {2}'.format(p.returncode, out, err))
            return None
        if is_cipher_file:
            return output_str
        return out.decode()

    def decrypt(self, output_str, input_str, is_plain_file=False, is_cipher_file=False):
        command = 'tpm2_rsadecrypt -c ' + self.child_obj

        if is_cipher_file:
            if not os.path.exists(input_str):
                print('Error: Input file doesn\'t exist, path = ' + input_str)
                return None
            command = command + ' ' + input_str
        else:
            command = 'echo -n \'' + input_str + '\' | base64 --decode | ' + command

        if is_plain_file:
            command = command + ' -o ' + output_str

        print('Decrypting...')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            print('Error[{0}]: Decryption failed, out = {1}, error = {2}'.format(p.returncode, out, err))
            return None
        if is_plain_file:
            return output_str
        return out.decode()

'''
### Test ###
os.makedirs('./data/', exist_ok=True)
tpm_helper = tpmHelper()

plain = 'This is the secret to be protected\nWhich has multiple lines'
with open('./data/plain', 'w') as f:
    f.write(plain)

print('------------------------------------------------------')
print('[Test 1] File to File')
tpm_helper.encrypt('./data/cipher', './data/plain', True, True)
tpm_helper.decrypt('./data/decrypted', './data/cipher', True, True)

print('Plain:')
with open('./data/plain') as f:
    for line in f:
        print(line, end='')
    print('')
print('Decrypted Cipher:')
with open('./data/decrypted') as f:
    for line in f:
        print(line, end='')
    print('')

print('------------------------------------------------------')
print('[Test 2] String to File')
tpm_helper.encrypt('./data/cipher', plain, False, True)
decrypted = tpm_helper.decrypt('', './data/cipher', False, True)

print('Plain:')
print(plain)
print('Decrypted Cipher:')
print(decrypted)

print('------------------------------------------------------')
print('[Test 3] File to String')
cipher = tpm_helper.encrypt('', './data/plain', True, False)
tpm_helper.decrypt('./data/decrypted', cipher, True, False)

print('Plain:')
with open('./data/plain') as f:
    for line in f:
        print(line, end='')
    print('')
print('Decrypted Cipher:')
with open('./data/decrypted') as f:
    for line in f:
        print(line, end='')
    print('')

print('------------------------------------------------------')
print('[Test 4] String to String')
cipher = tpm_helper.encrypt('', plain, False, False)
decrypted = tpm_helper.decrypt('', cipher, False, False)

print('Plain:')
print(plain)
print('Decrypted Cipher:')
print(decrypted)
'''

