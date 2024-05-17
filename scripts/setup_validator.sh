#!/bin/bash


# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}


check_mnemonic() {
    if [ -z "$MNEMONIC" ]; then
        echo "MNEMONIC variable is not set. Exiting"
        echo "Please set the MNEMONIC variable to the mnemonic of the wallet"
        echo "Example: export MNEMONIC='word1 word2 word3 ...'"
        exit 1
    fi
}


# Function to install Docker
install_docker() {
    if ! command_exists docker; then
        echo "Installing Docker"
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
        sudo -E apt update
        sudo -E apt install docker-ce -y
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker "$USER"
    else
        echo "Docker is already installed"
    fi
}



# Function to install Node.js and PM2
install_node_pm2() {
    if ! command_exists nvm; then
        echo "Installing Node.js and PM2"
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
        source ~/.nvm/nvm.sh
        nvm install --lts
        npm install -g pm2
    else
        echo "NVM is already installed"
    fi
}


# Function to clone and set up HIP Subnet
setup_hip_subnet() {
    echo "Setting up HIP Subnet"
    cd ~ || exit
    if [ ! -d "HIP-Subnet" ]; then
        git clone https://github.com/HIP-Labs/HIP-Subnet
    else
        cd HIP-Subnet || exit
        git reset --hard
        git checkout feat/llm-generation
        git pull
        cd ..
    fi
}

setup_gpu() {
    echo "Installing NVIDIA drivers"
    sudo apt install nvidia-driver-470 -y
    sudo apt install nvidia-cuda-toolkit -y
    echo "Verifying NVIDIA driver installation"
    nvidia-smi
    
    echo "Verifying CUDA installation"
    nvcc --version
}

# Function to install Python 3.10 and set up virtual environment
setup_python() {
    echo "Installing Python 3.10"
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo-E apt update
    sudo -E apt install -y python3.10 python3.10-venv python3.10-dev
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
}


setup_wallet() {
    if ! command_exists btcli; then
        echo "Btcli not found. Exiting"
        exit 1
    else
        # if MNEMONIC variable is not set, throw an error
        check_mnemonic
        btcli wallet regen_coldkey --wallet.name default --wallet.hotkey default --subtensor.network test --no_password --no_prompt --mnemonic $MNEMONIC
        btcli wallet regen_hotkey --wallet.name default --wallet.hotkey default --subtensor.network test --no_password --no_prompt --mnemonic $MNEMONIC
    fi
}


check_mnemonic
echo "Setting up Subtensor Testnet"
echo "Installing dependencies"
sudo -E apt update
sudo -E apt install -y apt-transport-https ca-certificates curl software-properties-common build-essential tmux dkms

install_docker

docker compose down --volumes

install_node_pm2

echo "Setting up GPU"
setup_gpu

echo "Running Subtensor Testnet in Docker"
cd ~ || exit

git clone https://github.com/opentensor/subtensor.git
cd subtensor || exit
git checkout main
sudo ./scripts/run/subtensor.sh -e docker --network testnet --node-type lite
setup_hip_subnet

cd ~/HIP-Subnet || exit
setup_python

echo "Creating virtual environment and installing HIP Subnet"
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

setup_wallet

echo "HIP Subnet setup complete"
echo "\n\n"
echo "Note:"
echo "Run the following command to setup the python env:"
echo "$ cd ~/HIP-Subnet && source venv/bin/activate"
echo "Now ensure that your coldkey has enough Tao to register and stake to become a validator."
echo "Run the following command to check your balance:"
echo "$ btcli w balance --wallet.name default --subtensor.network test --wallet.path ~/.bittensor/wallets/ --no_prompt"
echo "Run the following command to register to the subnet:"
echo "$ btcli subnet register --wallet.name default --wallet.hotkey default --subtensor.network test --no_prompt --netuid 134"
echo "Run the following command to start the server:"
echo "$ python neurons/validator.py"