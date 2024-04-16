#!/bin/bash

# Ensure the script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi


# Install Rust and Subtensor
cd ~
apt-get update
apt install --assume-yes software-properties-common make build-essential git clang curl libssl-dev llvm libudev-dev protobuf-compiler tree jq
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
git clone https://github.com/opentensor/subtensor.git ~/subtensor
cd ~/subtensor
bash ./scripts/init.sh
cargo build --release --features pow-faucet
BUILD_BINARY=0 ./scripts/localnet.sh 


# Install Subnet and Bittensor
# Upgrade Bittensor
add-apt-repository ppa:deadsnakes/ppa -y
apt-get install -y python3.10 python3.10-venv python3.10-dev
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

git clone https://github.com/HIP-Labs/HIP-Subnet ~/HIP-Subnet
cd ~/HIP-Subnet
if [ -f "setup.py" ]; then
    # Create a Python virtual environment and activate it
    python3 -m venv venv
    source venv/bin/activate

    # Install dependencies and setup the package in editable mode
    pip install -e .
else
    echo "setup.py not found in the repository."
    exit 1
fi

# Install npm and pm2
sudo apt update && sudo apt install npm && sudo npm install pm2 -g && pm2 update

