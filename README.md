# Bittensor Subnet  #36

---
Please submit issues and pull requests through this repo.
---

# HIP (Human Intelligence Primitive) Subnet

> The HIP (Human Intelligence Primitive) Subnet is a [Bittensor](https://github.com/opentensor/bittensor) subnet designed to provide human intelligence services to other subnets. It will allow other subnets to send their data to the HIP Subnet for human evaluation, testing, and feedback. The HIP Subnet harnesses the collective intelligence of human miners who compete to provide high-quality evaluations and insights on the submitted data. Validators in the HIP Subnet assess the quality of the miners' responses and distribute rewards accordingly, creating an incentive mechanism that promotes diverse and valuable human feedback.


## Features

 ##### Human Intelligence Primitives: 
 > The HIP Subnet leverages human intelligence to perform tasks that require subjective judgment, contextual understanding, and creative problem-solving. Miners in the HIP Subnet are human participants who contribute their cognitive abilities to evaluate and provide feedback on data submitted by other subnets.


 ##### Incentive Mechanism: 
 > The HIP Subnet implements an incentive mechanism that rewards miners for providing high-quality evaluations and feedback. Miners compete to offer the most valuable insights, and the subnet's validators distribute rewards based on the quality and human-likeness of the miners' responses. This incentive structure encourages miners to deliver their best work and continuously improve the networks overall performance.


---


# Getting Started

<em>note: Bittensor is currently supported on macOS and Linux with limited support for Windows.</em>

To participate in the HIP Subnet as a miner or validator, follow these steps:


# Mining

Mining in the HIP Subnet is designed to be straightforward. Follow these steps to set up and run your miner on an Ubuntu server.

## Prerequisites

- Python 3.8 or higher
- A Bittensor wallet with sufficient TAO for staking and registration
- 2X VCPU
- 8GB RAM
- 100GB SSD

## Setting Up the Miner

1. **Clone the HIP Subnet repository:**
    ```bash
    git clone https://github.com/HIP-LABS/HIP-Subnet.git
    ```
2. **Enter the directory where the HIP Subnet was cloned:**
    ```bash
    cd HIP-Subnet
    ```

3. **Create a virtual environment and install dependencies:**
    ```bash
    sudo apt-get update
    sudo apt install python3.10-venv
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -e .
    ```

4. **Register your Bittensor keys with the subnet:**
    ```bash
    btcli subnet register --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --netuid 36 --subtensor.network finney
    ```
    Replace `<YOUR_WALLET_COLDKEY>` and `<YOUR_WALLET_HOTKEY>` with your corresponding keys.

5. **Confirm your key is registered to the subnet:**
    ```bash
    btcli w inspect --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --netuid 36 --subtensor.network finney
    ```

## Running the Miner

To ensure that the miner and server run continuously, we will use `pm2`.

1. **Install Node.js and `pm2`:**
    ```bash
    sudo apt-get install -y nodejs npm
    sudo npm install pm2@latest -g
    ```

2. **Ensure your virtual environment is activated:**
    ```bash
    source venv/bin/activate
    ```

3. **Run the miner server with `pm2`:**
    ```bash
    pm2 start ./scripts/run_miner_frontend.sh --name miner_server
    ```

4. **Run the miner script with `pm2`:**
    ```bash
    pm2 start python3 --name miner -- neurons/miner.py --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --netuid 36 --subtensor.network finney --logging.debug --logging.trace
    ```

5. **Save the `pm2` process list and corresponding environments:**
    ```bash
    pm2 save
    ```

6. **Set `pm2` to start on boot:**
    ```bash
    pm2 startup
    ```

## Accessing the Miner Frontend

The miner frontend will be accessible at `http://localhost:3001` from your chosen web browser.

## Managing `pm2` Processes

- To check the status of your processes:
    ```bash
    pm2 status
    ```

- To restart a process:
    ```bash
    pm2 restart <process_name>
    ```

- To stop a process:
    ```bash
    pm2 stop <process_name>
    ```

For further assistance, refer to the [PM2 documentation](https://github.com/Unitech/pm2) to manage and keep your miner application online 24/7.

---

# Validator

Setting up a HIP validator involves configuring a server with specific hardware requirements. Follow these steps to set up and run your validator on an Ubuntu server.

## Prerequisites

- 2x NVIDIA RTX 3090
- 8X VCPU
- 32GB RAM
- 200GB NVMe
- Python 3.8 or higher
- A Bittensor wallet with sufficient TAO for staking and registration

## Option 1: Automated Setup

1. **SSH into your server:**
    ```bash
    ssh username@your-server-ip
    ```

2. **Export the mnemonic for your validator keys:**
    ```bash
    export MNEMONIC="[generate a mnemonic to use as validator]"
    ```

3. **Run the setup script:**
    ```bash
    curl https://raw.githubusercontent.com/HIP-Labs/HIP-Subnet/main/scripts/setup_validator.sh | bash
    ```

4. **Restart the server:**
    ```bash
    sudo reboot
    ```

5. **SSH into the server again:**
    ```bash
    ssh username@your-server-ip
    ```

6. **Spool up the subtensor after reboot:**
    ```bash
    cd ~/subtensor
    sudo ./scripts/run/subtensor.sh -e docker --network finney --node-type lite
    ```

7. **Change directory back into the HIP-Subnet and activate the environment:**
    ```bash
    cd ~/HIP-Subnet
    source venv/bin/activate
    ```

8. **Ensure your GPU is working:**
    ```bash
    python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
    ```

## Option 2: Manual Setup

1. **SSH into your server:**
    ```bash
    ssh username@your-server-ip
    ```

2. **Install NVIDIA drivers and CUDA toolkit:**
    ```bash
    sudo apt update
    sudo apt install nvidia-driver-535 -y
    sudo apt install nvidia-cuda-toolkit -y
    ```

3. **Install Docker:**
    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
    sudo apt update
    sudo apt install docker-ce -y
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker "$USER"
    ```

4. **Install Node.js and PM2:**
    ```bash
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    source ~/.nvm/nvm.sh
    nvm install --lts
    npm install -g pm2
    ```

5. **Clone and set up HIP Subnet:**
    ```bash
    cd ~
    git clone https://github.com/HIP-Labs/HIP-Subnet
    cd HIP-Subnet
    git reset --hard
    git checkout main
    git pull
    ```

6. **Install Python 3.10 and set up virtual environment:**
    ```bash
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3.10-dev
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    ```

7. **Create virtual environment and install dependencies:**
    ```bash
    cd ~/HIP-Subnet
    python3.10 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -e .
    ```

8. **Run the subtensor in Docker:**
    ```bash
    cd ~
    git clone https://github.com/opentensor/subtensor.git
    cd subtensor
    git checkout main
    sudo ./scripts/run/subtensor.sh -e docker --network finney --node-type lite
    ```

## Staking and Running the Validator

1. **Stake your validator:**
    ```bash
    btcli subnet stake --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --amount <DESIRED_AMOUNT_OF_TAO> --netuid 36 --subtensor.network finney
    ```

2. **Run the validator script with `pm2`:**
    ```bash
    pm2 start python3 --name validator -- neurons/validator.py --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --netuid 36 --subtensor.network finney --logging.debug --logging.trace
    ```

3. **Save the `pm2` process list and corresponding environments:**
    ```bash
    pm2 save
    ```

4. **Set `pm2` to start on boot:**
    ```bash
    pm2 startup
    ```

## Managing `pm2` Processes

- To check the status of your processes:
    ```bash
    pm2 status
    ```

- To restart a process:
    ```bash
    pm2 restart <process_name>
    ```

- To stop a process:
    ```bash
    pm2 stop <process_name>
    ```

For further assistance, refer to the [PM2 documentation](https://github.com/Unitech/pm2) to manage and keep your validator application online 24/7.

---

##### Contributing

We welcome contributions to the HIP Subnet! If you'd like to contribute, please follow these steps:

 - Fork the repository
 - Create a new branch for your feature or bug fix
 - Make your changes and commit them with descriptive messages
 - Push your changes to your forked repository
 - Submit a pull request to the main repository
 - Please ensure that your code adheres to the project's coding style and passes all tests before submitting a pull request.

---

```
#### License

# The MIT License (MIT)
# Copyright © 2024 HIP-LABS 

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
```
