# PUBLIC TESTNET UID #134

---

# HIP (Human Intelligence Primitive) Subnet

> The HIP (Human Intelligence Primitive) Subnet is a [Bittensor](https://github.com/opentensor/bittensor) subnet designed to provide human intelligence services to other subnets. It will allow other subnets to send their data to the HIP Subnet for human evaluation, testing, and feedback. The HIP Subnet harnesses the collective intelligence of human miners who compete to provide high-quality evaluations and insights on the submitted data. Validators in the HIP Subnet assess the quality of the miners' responses and distribute rewards accordingly, creating an incentive mechanism that promotes diverse and valuable human feedback.


## Features

 ##### Human Intelligence Primitives: 
 > The HIP Subnet leverages human intelligence to perform tasks that require subjective judgment, contextual understanding, and creative problem-solving. Miners in the HIP Subnet are human participants who contribute their cognitive abilities to evaluate and provide feedback on data submitted by other subnets.


 ##### Incentive Mechanism: 
 > The HIP Subnet implements an incentive mechanism that rewards miners for providing high-quality evaluations and feedback. Miners compete to offer the most valuable insights, and the subnet's validators distribute rewards based on the quality and human-likeness of the miners' responses. This incentive structure encourages miners to deliver their best work and continuously improve the networks overall performance.


---


## Getting Started

NOTE - Bittensor is currently supported on macOS and Linux with limited support for Windows.

To participate in the HIP Subnet as a miner or validator, follow these steps:

##### Prerequisites

 - Python 3.8 or higher
   
 - A Bittensor wallet with sufficient TAO for staking and registration

##### Installation

Clone the HIP Subnet repository:
```
git clone https://github.com/HIP-LABS/HIP-Subnet.git
```
Enter the directory where the hip subnet was cloned:
```
cd HIP-Subnet
```
Once inside the HIP-Subnet directory, there are two ways to install the subnet. 

1. The scripted installation can be activated with:
```
chmod +x scripts/hip_install.sh
./scripts/hip_install.sh
```
After completing the steps above, ensure you activate the enviroment created:
```
source env/bin/activate
```
# OR

2. Manual installation:

create the enviroment and Install the required dependencies with:
```
sudo apt-get update
sudo apt install python3.10-venv
python3 -m venv env 

```
After completing the steps above, ensure you activate the enviroment created:
```
source env/bin/activate
```
Complete the installation process with following command:
```
python3 -m pip install -e .
```
To confirm you are in the enviroment created, you will see a little (env) on the left hand side of your username within the terminal.
`(env) (base) user@root:~/HIP-Subnet$`

---

## Participating 

Now that the installation is complete it is now time to participate in the network as a miner or validator.
First you must register with the subnet on testnet in order to participate as a miner or validator.

Register your bittensor keys with: 
```
btcli subnet register
--wallet.name <YOUR_WALLET_COLDKEY>
--wallet.hotkey <YOUR_WALLET_HOTKEY>
--netuid 134
--subtensor.network test
```

You can confirm your key is registered to the subnet with the following command:
```
btcli w inspect
--wallet.name <YOUR_WALLET_COLDKEY>
--wallet.hotkey <YOUR_WALLET_HOTKEY>
--netuid 134
--subtensor.network test
```

##### Mining

Mining can be run on any device within the local network once the miner script is executed. However, there are a few considerations and steps to ensure that the miner can be accessed and utilized effectively across the local network:

 - Ensure that the device running the miner script is connected to the local network and has a stable network connection.
 - Configure the network settings to allow incoming connections to the miner's frontend web application port (port 3001 is the default).
 - If the local network has a firewall or security measures in place, make sure to open the necessary ports or create appropriate firewall rules to allow communication with the miner.

NOTE - during this testing phase it is suggested you run your miner and frontend scripts, in tmux sessions.
tmux is a terminal multiplexer. It lets you switch easily between several programs in one terminal, detach them (they keep running in the background) and reattach them to a different terminal. You can visit the repo [here](https://github.com/tmux/tmux/wiki) and follow the official guides if you require assistance.


Run the miner after your keys have been registered: 
```
python3 neurons/miner.py
--wallet.name <YOUR_WALLET_COLDKEY>
--wallet.hotkey <YOUR_WALLET_HOTKEY>
--netuid 134
--subtensor.network test
--logging.debug
--logging.trace
```
To run the miner frontend script, follow these steps:

 - Open a terminal or command prompt.
 - Navigate to the HIP-Subnet root directory.
 - Make sure the run_miner_frontend.sh script has execute permissions. If not, you can add execute permissions using the following command:
   ```
   chmod +x scripts/run_miner_frontend.sh
   ```
 - Run the script by executing the following command:
   ```
   ./scripts/run_miner_frontend.sh
   ```

  The script will ensure port 3001 is open and start the frontend server. You should see output similar to the following:

```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:3001 (Press CTRL+C to quit)
```
 - This indicates that the miner's frontend is now running and accessible at http://localhost:3001.
 - You can now access the miner's frontend by opening a web browser and navigating to http://localhost:3001. 
 - To stop the miner's frontend, press CTRL+C in the terminal where the script is running.

---

##### Validating

NOTE - during this testing phase it is suggested you run your validator script in a tmux session.
tmux is a terminal multiplexer. It lets you switch easily between several programs in one terminal, detach them (they keep running in the background) and reattach them to a different terminal. You can visit the repo [here](https://github.com/tmux/tmux/wiki) and follow the official guides if you require assistance.


Stake your validator:
```
btcli subnet stake 
--wallet.name <YOUR_WALLET_COLDKEY> 
--wallet.hotkey <YOUR_WALLET_HOTKEY> 
--amount <DESIRED_AMOUNT_OF_TAO> 
--netuid 134
--subtensor.network test
```
Run the validator:
```
python3 neurons/validator.py 
--wallet.name <YOUR_WALLET_COLDKEY> 
--wallet.hotkey <YOUR_WALLET_HOTKEY> 
--netuid 134 
--subtensor.network test 
--logging.debug
--logging.trace
```
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
