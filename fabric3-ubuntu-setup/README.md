# fabric3-ubuntu-setup

This script sets up a base Ubuntu 16.04 AWS EC2 instance with:
1. Docker CE
2. docker-compose
3. 2GB swap space
4. Default firewall (UFW) settings, opening ports 80 and 443

The script requires the follow environment variables to be set:
1. **SSH_HOST** : use Fabric's ssh host string user@host:port
2. **SSH_KEY** : the SSH private key file (.pem) in string format
3. **SSH_SUDO_PASS** : the sudo user's password on the remote host

Setup your python environment, install pip requirements:
```
python3.6 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```


To run the script, replace the values in "< ... >" with actual values:
```
export SSH_HOST="<ssh_host_string>"
export SSH_KEY="<ssh_key_file_string_value>"
export SSH_SUDO_PASS="<ssh_sudo_pass>"
fab setup
```
