# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2024 HIP Labs

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


import time
from typing import List
import torch

# Bittensor
import bittensor as bt

# Bittensor Validator Template:
from hip.utils.misc import get_utc_timestamp
from hip.validator import forward

# import base validator class which takes care of most of the boilerplate
from hip.base.validator import BaseValidatorNeuron
from hip.validator.reward import linear_rewards
from hip.version import check_updates

# The public API imports
import asyncio
from hip.hip_public_api import app as hip_public_api
import uvicorn


class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)
        self.public_api_task = None

        bt.logging.info("load_state()")
        self.load_state()

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Fetch the task
        - Send the task to the miners
        - Get the responses
        - Reward the miners
        - Updating the scores
        """
        return await forward(self)
    
    def start_public_api(self): # Start the api for external sources to submit tasks to. Probably need more security measures. I dunno, it's a start.
        config = uvicorn.Config(hip_public_api, host="0.0.0.0", port=69420, log_level="info")
        server = uvicorn.Server(config)
        self.public_api_task = asyncio.create_task(server.serve())

    async def run_with_api(self):
        self.start_public_api()
        try:
            while True:
                await self.forward()
                await asyncio.sleep(self.config.neuron.task_gen_step)
        finally:
            if self.public_api_task:
                self.public_api_task.cancel()
                await self.public_api_task

# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    updateAvailable = check_updates()
    if updateAvailable:
        bt.logging.info("Update available. Please update the validator.")
        print("Update available. Please update the validator.")
        exit(1)
    with Validator() as validator:
        while True:
            asyncio.run(validator.run_with_api()) # Run the validator with the api, comment this out if you don't wanna use it.
            bt.logging.info(f"Validator running... {get_utc_timestamp()}")
            time.sleep(5)


