echo "Setting up Subtensor Testnet"
echo "Installing dependencies"
sudo apt update >/dev/null 2>&1
sudo apt install apt-transport-https ca-certificates curl software-properties-common tmux -y >/dev/null 2>&1

echo "Installing Docker"
# check if docker is installed and install it if not
if ! [ -x "$(command -v docker)" ]; then
    echo "Docker is not installed. Installing Docker"
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg >/dev/null 2>&1
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null 2>&1
    sudo apt update >/dev/null 2>&1
    sudo apt install docker-ce -y >/dev/null 2>&1
    sudo systemctl start docker >/dev/null 2>&1
    sudo systemctl enable docker >/dev/null 2>&1
    sudo usermod -aG docker ${USER}
else
    echo "Docker is already installed"
fi
docker compose down --volumes

echo "Installing Node.js and PM2"
# check if nvm and pm2 are installed and install them if not
if ! [ -x "$(command -v nvm)" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    source ~/.nvm/nvm.sh
    nvm install --lts
    npm install -g pm2
else
    echo "NVM is already installed"
fi

echo "Running Subtensor Testnet in Docker"
cd ~
git clone https://github.com/opentensor/subtensor.git
cd subtensor
git checkout main
sudo ./scripts/run/subtensor.sh -e docker --network testnet --node-type lite

echo "Setting up HIP Subnet"
cd ~
if [ ! -d "HIP-Subnet" ]; then
    git clone https://github.com/HIP-Labs/HIP-Subnet
    cd HIP-Subnet
else
    cd HIP-Subnet
    git reset --hard
    git checkout main
    git pull
    cd ..
fi

echo "Installing Python 3.10"
# only install python3.10 if it is not already installed
if ! [ -x "$(command -v python3.10)" ]; then
    sudo add-apt-repository ppa:deadsnakes/ppa -y >/dev/null 2>&1
    sudo apt install -y python3.10 python3.10-venv python3.10-dev >/dev/null 2>&1
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 >/dev/null 2>&1
else
    echo "Python 3.10 is already installed"
fi
echo "Creating virtual environment and installing HIP Subnet"
python3.10 -m venv venv >/dev/null 2>&1
source venv/bin/activate >/dev/null 2>&1
pip install -e . >/dev/null 2>&1

echo "HIP Subnet setup complete"
echo "Running HIP Subnet"
echo "Run the following command:"
echo "cd ~/HIP-Subnet && source venv/bin/activate"
echo "Now ensure the wallet is configured and run the following commands:"
echo "pm2 start ecosystem.config.js"
