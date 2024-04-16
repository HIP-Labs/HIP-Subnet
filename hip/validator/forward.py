# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

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

import bittensor as bt

from hip.protocol import TaskSynapse
from hip.validator.reward import get_rewards
from hip.utils.uids import get_random_uids
from hip.utils.hip_service import get_task

import time


async def forward(self):
    """
    The forward function is called by the validator every time step. In our case it is called every 10 seconds.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.
    """
    firstTime = False
    # task_gen_step is the wait time between creating and sending tasks.
    task_gen_step = self.config.neuron.task_gen_step

    # Store the last run time
    if not hasattr(self, "_last_run_time"):
        firstTime = True
        self._last_run_time = time.time()

    # Check if 10 seconds have passed
    if time.time() - self._last_run_time < task_gen_step and not firstTime:
        return
    self._last_run_time = time.time()

    print("Forwarding")

    miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
    task = await get_task()
    # The dendrite client queries the network.
    responses = await self.dendrite(
        # Send the query to selected miner axons in the network.
        axons=[self.metagraph.axons[uid] for uid in miner_uids],
        synapse=task,
        # All responses have the deserialize function called on them before returning.
        # You are encouraged to define your own deserialization function.
        deserialize=True,
    )
    # Log the results for monitoring purposes.
    bt.logging.info(f"Received responses: {responses}")

    # TODO(developer): Define how the validator scores responses.
    # Adjust the scores based on responses from miners.
    rewards = get_rewards(self, task=task, responses=responses)
    for idx, response in enumerate(responses):
        print(f"Response {idx}: Reward: {rewards[idx]} {response.answer}")
    bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
    self.update_scores(rewards, miner_uids)
