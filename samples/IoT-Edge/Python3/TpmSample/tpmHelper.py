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

    def encrypt(self, output_path, input_plain, is_plain_file=False):
        if is_plain_file and not os.path.exists(input_plain):
            print("Error: Input file doesn't exist, path = " + input_plain)
            return None

        command = 'tpm2_rsaencrypt -c ' + self.child_obj + ' -o ' + output_path
        if is_plain_file:
            command = command + ' ' + input_plain
        else:
            command = 'echo -n \'' + input_plain + '\' | ' + command

        print('Encrypting...')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = p.communicate()

        if p.returncode != 0:
            print('Error[{0}]: Encryption failed, out = {1}, error = {2}'.format(p.returncode, out, err))
            return None
        if is_plain_file:
            return output_path
        return out

    def decrypt(self, output_plain, input_path, is_plain_file=False):
        if not os.path.exists(input_path):
            print("Error: Input file doesn't exist, path = " + input_path)
            return None

        command = 'tpm2_rsadecrypt -c ' + self.child_obj + ' ' + input_path
        if is_plain_file:
            command = command + ' -o ' + output_plain

        print('Decrypting...')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = p.communicate()

        if p.returncode != 0:
            print('Error[{0}]: Decryption failed, out = {1}, error = {2}'.format(p.returncode, out, err))
            return None
        if is_plain_file:
            return output_plain
        return out

### Test ###
#os.makedirs('./data/', exist_ok=True)
#tpm_helper = tpmHelper()

#with open('./data/secret', 'w') as f:
#    f.write('My secret to be protected')

#tpm_helper.encrypt('./data/encrypted', './data/secret', True)
#os.remove('./data/secret')

#tpm_helper.decrypt('./data/decrypted', './data/encrypted', True)

#tpm_helper.encrypt('./data/encrypted', 'My secret!', False)
#print(tpm_helper.decrypt('', './data/encrypted', False))

