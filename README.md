# PUBLIC TESTNET UID #134

---

# HIP (Human Intelligence Primitive) Subnet

> The HIP (Human Intelligence Primitive) Subnet is a Bittensor subnet designed to provide human intelligence services to other subnets. It will allow other subnets to send their data to the HIP Subnet for human evaluation, testing, and feedback. The HIP Subnet harnesses the collective intelligence of human miners who compete to provide high-quality evaluations and insights on the submitted data. Validators in the HIP Subnet assess the quality of the miners' responses and distribute rewards accordingly, creating an incentive mechanism that promotes diverse and valuable human feedback.


## Features

 ##### Human Intelligence Primitives: 
 > The HIP Subnet leverages human intelligence to perform tasks that require subjective judgment, contextual understanding, and creative problem-solving. Miners in the HIP Subnet are human participants who contribute their cognitive abilities to evaluate and provide feedback on data submitted by other subnets.


 ##### Incentive Mechanism: 
 > The HIP Subnet implements an incentive mechanism that rewards miners for providing high-quality evaluations and feedback. Miners compete to offer the most valuable insights, and the subnet's validators distribute rewards based on the quality and human-likeness of the miners' responses. This incentive structure encourages miners to deliver their best work and continuously improve the networks overall performance.


---


## Getting Started

To participate in the HIP Subnet as a miner or validator, follow these steps:

##### Prerequisites

 - Python 3.8 or higher

 - Bittensor installed:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/opentensor/bittensor/master/scripts/install.sh)"
```
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
Once inside the HIP-Subnet directory, create the enviroment and Install the required dependencies with:
```
sudo apt get update
sudo apt install python3.10-venv
python3 -m venv env 
source env/bin/activate
python3 -m pip install -e .
```

---

## Participating 

Now that the installation is complete it is now time to participate in the network as a miner or validator.

##### Mining

Mining can be run on any device within the local network once the miner script is executed. However, there are a few considerations and steps to ensure that the miner can be accessed and utilized effectively across the local network:
 - Ensure that the device running the miner script is connected to the local network and has a stable network connection.
 - Configure the network settings to allow incoming connections to the miner's frontend web application port (port 3001 is the default).
 - If the local network has a firewall or security measures in place, make sure to open the necessary ports or create appropriate firewall rules to allow communication with the miner.


Register your miner: 
```
btcli register --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --netuid 134 --subtensor.network test
```
Run the miner: 
```
python3 neurons/miner.py --netuid 134 --subtensor.network test --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --logging.debug
```
To run the miner frontend script, follow these steps:

 - Open a terminal or command prompt.
 
 - Navigate to the directory where the run_miner_frontend.sh script is located. eg. `cd /path/to/HIP-Subnet`

 - Make sure the run_miner_frontend.sh script has execute permissions. If not, you can add execute permissions using the following command: `chmod +x run_miner_frontend.sh`

 - Run the script by executing the following command: `./run_miner_frontend.sh`

  The script will start the frontend server, and you should see output similar to the following:

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

Register your validator:
```
btcli register --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --netuid 134 --subtensor.network test
```
Stake your validator:
```
btcli stake --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --amount 100 --netuid 134 --subtensor.network test
```
Run the validator:
```
python3 neurons/validator.py --netuid 134 --subtensor.network test --wallet.name <YOUR_WALLET_COLDKEY> --wallet.hotkey <YOUR_WALLET_HOTKEY> --logging.debug
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

#### License
```
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
