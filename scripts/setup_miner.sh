#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_MODE=a
export NEEDRESTART_SUSPEND=1

#    ___ ___  _  _ ___ _____ _   _  _ _____ ___
#   / __/ _ \| \| / __|_   _/_\ | \| |_   _/ __|
#  | (_| (_) | .` \__ \ | |/ _ \| .` | | | \__ \
#   \___\___/|_|\_|___/ |_/_/ \_\_|\_| |_| |___/
#
NODE_VERSION="20.14.0"
PYTHON_VERSION="python3.10"
GITHUB_REPO_URL="https://github.com/HIP-Labs/HIP-Subnet"

#   __  __ ___ _____ _  _  ___  ___  ___
#  |  \/  | __|_   _| || |/ _ \|   \/ __|
#  | |\/| | _|  | | | __ | (_) | |) \__ \
#  |_|  |_|___| |_| |_||_|\___/|___/|___/

stop_all_services() {
    # Stop the frontend service if it is running or installed
    if sudo systemctl is-active --quiet uvicorn_frontend; then
        sudo systemctl stop uvicorn_frontend
        # now disable the service
        sudo systemctl disable uvicorn_frontend
    fi
    # there is a chance that nvm is not configured in the current shell
    if [ -f ~/.nvm/nvm.sh ]; then
        source ~/.nvm/nvm.sh
    fi
    if command_exists pm2; then
        pm2 stop all
        pm2 unstartup
        pm2 delete all
    fi
}

check_supported_os() {
    # Check if the operating system is Ubuntu
    if [[ $(lsb_release -si) != "Ubuntu" ]]; then
        echo "Operating system not supported"
        exit 1
    fi

    # Check the Ubuntu version
    VERSION=$(lsb_release -sr)
    if [[ $VERSION != "22.04" ]]; then
        echo "OS version not supported"
        exit 1
    fi

    # Continue with the rest of the script if both conditions are met
    echo "Operating system and version are supported"
}

install_python() {
    if ! command_exists $PYTHON_VERSION; then
        echo "Installing Python 3.10"
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt update
        sudo apt install -y $PYTHON_VERSION $PYTHON_VERSION-venv $PYTHON_VERSION-dev python3-pip
        sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10
        if [ -d "$HOME/.local/bin" ]; then
            echo "export PATH=$HOME/.local/bin:$PATH" >>~/.bashrc
            source ~/.bashrc
        fi
    else
        echo "Python 3.10 is already installed"
    fi
}

install_node_pm2() {
    source ~/.bashrc
    if ! command_exists nvm; then
        echo "Installing Node.js and PM2"
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
        source ~/.nvm/nvm.sh
        nvm install $NODE_VERSION
        nvm use $NODE_VERSION
        nvm alias default $NODE_VERSION
        npm install -g pm2
        pm2 install pm2-logrotate
        pm2 startup
        pm2 save
    else
        echo "NVM is already installed"
        nvm install $NODE_VERSION
        nvm use $NODE_VERSION
        nvm alias default $NODE_VERSION
        npm install -g pm2
        pm2 install pm2-logrotate
        pm2 startup
        pm2 save
    fi
}

setup_subnet() {
    # check if git is installed
    if ! command_exists git; then
        sudo apt install -y git
    fi
    if [ -d ~/HIP-Subnet ]; then
        rm -rf ~/HIP-Subnet
    fi
    git clone $GITHUB_REPO_URL ~/HIP-Subnet
}

install_requirements() {
    if [ -f ~/HIP-Subnet/requirements.txt ]; then
        cd ~/HIP-Subnet &&
            pip install -r requirements.txt &&
            pip install -e .
    else
        echo "requirements.txt not found"
    fi
}

setup_wallet() {
    echo "Creating wallet"
    if [ -d ~/.bittensor/wallets ]; then
        echo "Wallet already exists"

    else
        btcli w new_coldkey --wallet.name default --no_password --no_prompt &&
            btcli w new_hotkey --wallet.name default --wallet.hotkey default --no_password --no_prompt
    fi
}

setup_frontend() {
    if [ -f /etc/nginx/sites-enabled/reverse-proxy ]; then
        echo "frontend already setup"
        pm2 stop frontend
        pm2 delete frontend
        pm2 start uvicorn --name frontend --interpreter python -- frontend:app --host 0.0.0.0 --port 5001
    else
        cd ~/HIP-Subnet/ &&
            pm2 start uvicorn --name frontend --interpreter python -- frontend:app --host 0.0.0.0 --port 5001 &&
            sudo apt install -y nginx &&
            sudo bash -c 'cat <<EOF > /etc/nginx/sites-available/reverse-proxy
server {
    listen 80;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF'
        sudo rm /etc/nginx/sites-enabled/default
        # Enable the reverse proxy configuration
        sudo ln -s /etc/nginx/sites-available/reverse-proxy /etc/nginx/sites-enabled/
        sudo nginx -t
        # If the test passes, reload Nginx to apply changes
        if [ $? -eq 0 ]; then
            sudo systemctl reload nginx
            echo "Nginx configuration reloaded successfully."
        else
            echo "Nginx configuration test failed. Please check the configuration and try again."
        fi
    fi
}

#   __  __   _   ___ _  _   ___  ___ ___ ___ ___ _____
#  |  \/  | /_\ |_ _| \| | / __|/ __| _ \_ _| _ \_   _|
#  | |\/| |/ _ \ | || .` | \__ \ (__|   /| ||  _/ | |
#  |_|  |_/_/ \_\___|_|\_| |___/\___|_|_\___|_|   |_|
#

sudo apt update
install_node_pm2
install_python
setup_subnet
install_requirements

setup_wallet
setup_frontend

echo "RUN:"
echo "btcli subnet register --netuid 36  --wallet.name default --wallet.hotkey default --no_prompt"
echo "cd ~/HIP-Subnet && pm2 start neurons/miner.py --name miner --interpreter python --  --netuid 36  --wallet.name default --wallet.hotkey default && pm2 save"
