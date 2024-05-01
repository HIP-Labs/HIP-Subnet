echo "Setting up Subtensor Testnet"
echo "Installing dependencies"
sudo apt update > /dev/null 2>&1
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y > /dev/null 2>&1
echo "Installing Docker"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg > /dev/null 2>&1
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 2>&1
sudo apt update > /dev/null 2>&1
sudo apt install docker-ce -y > /dev/null 2>&1
sudo systemctl start docker > /dev/null 2>&1
sudo systemctl enable docker > /dev/null 2>&1
sudo usermod -aG docker ${USER}
docker compose down --volumes

echo "Installing Node.js and PM2"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.nvm/nvm.sh
nvm install --lts
npm install -g pm2

echo "Running Subtensor Testnet in Docker"
cd ~
git clone https://github.com/opentensor/subtensor.git
cd subtensor
git checkout main
sudo ./scripts/run/subtensor.sh -e docker --network testnet --node-type lite


echo "Setting up HIP Subnet"
cd ~
git clone https://github.com/HIP-Labs/HIP-Subnet
cd HIP-Subnet
sudo add-apt-repository ppa:deadsnakes/ppa -y > /dev/null 2>&1
sudo apt install -y python3.10 python3.10-venv python3.10-dev > /dev/null 2>&1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 > /dev/null 2>&1
python3.10 -m venv venv > /dev/null 2>&1
source venv/bin/activate > /dev/null 2>&1
pip install -e . > /dev/null 2>&1

echo "Running HIP Subnet"
echo "First make sure the Subtensor Testnet is running"
echo "Then run the following commands:"
echo "source venv/bin/activate"
echo "pm2 start ecosystem.config.js"