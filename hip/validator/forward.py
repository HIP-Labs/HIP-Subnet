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

import random
import bittensor as bt

from hip.protocol import TaskSynapse
from hip.validator.image_generator import generate_image_task
from hip.validator.reward import get_rewards
from hip.utils.uids import get_random_uids
from hip.validator.hip_service import get_llm_task
from hip.validator.captcha_generator import generate_capcha
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

    # Check if task_gen_step seconds have passed
    if time.time() - self._last_run_time < task_gen_step and not firstTime:
        return
    self._last_run_time = time.time()

    miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
    captcha = generate_capcha()

    # Decide if image or llm task should be sent
    task_type = random.choice(["image", "llm"])
    if task_type == "image":
        task = generate_image_task(captcha=captcha["image"])
    else:
        task = get_llm_task(captcha=captcha["image"])

    print(f"Forwarding Task: {task.id} to miners: {miner_uids}")
    ground_truth = task.answer
    task.answer = ""

    # The dendrite client queries the network.
    responses = await self.dendrite(
        # Send the query to selected miner axons in the network.
        axons=[self.metagraph.axons[uid] for uid in miner_uids],
        synapse=task,
        timeout=self.config.neuron.timeout,
        # All responses have the deserialize function called on them before returning.
        # You are encouraged to define your own deserialization function.
        deserialize=True,
    )
    task.answer = ground_truth

    # Log the results for monitoring purposes.
    # bt.logging.info(f"Received responses: {responses}")
    # For each response print the response's id and the response's answer.
    for response in responses:
        print(
            f"Response from {response.axon.hotkey}: {response.answer} Code: {response.dendrite.status_code} Message: {response.dendrite.status_message} Task ID: {response.id}"
        )
    # TODO(developer): Define how the validator scores responses.
    # Adjust the scores based on responses from miners.
    rewards = get_rewards(
        self, task=task, responses=responses, captcha_ground_truth=captcha["text"]
    )
    print(f"Rewards: {rewards}")
    bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
    self.update_scores(rewards, miner_uids)
