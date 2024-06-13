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
from hip.validator import forward

# import base validator class which takes care of most of the boilerplate
from hip.base.validator import BaseValidatorNeuron
from hip.validator.reward import linear_rewards
from hip.version import check_updates


class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

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

    def update_scores(
        self, rewards: torch.FloatTensor, uids: List[int], question_type: str
    ):
        current_time = time.time()

        for uid, reward in zip(uids, rewards):
            if uid not in self.rewards_log:
                self.rewards_log[uid] = []
            self.rewards_log[uid].append((reward.item(), current_time, question_type))

        for uid in uids:
            # Filter rewards for the last 24 hours
            recent_rewards = [
                (r, t, qtype)
                for r, t, qtype in self.rewards_log[uid]
                if current_time - t <= 86400
            ]

            # Separate regular questions and captchas
            correct_answers = sum(1 for r, t, qtype in recent_rewards if r == 1.0)
            captcha_penalties = sum(
                1 for r, t, qtype in recent_rewards if qtype == "captcha" and r == 0.0
            )
            wrong_answers = sum(
                1 for r, t, qtype in recent_rewards if r == 0.0 and qtype != "captcha"
            )

            # For each wrong answer, penalize the score by 1% by computing the penalty
            # as 1% of the total number of wrong answers
            for i in range(wrong_answers):
                score = score * 1

            # For each wrong captcha answer, penalize the score by 5% by computing the penalty
            # as 5% of the total number of failed captchas
            score = linear_rewards(self, correct_answers)
            for i in range(captcha_penalties):
                score = score * 0.95

            # Update the scores tensor
            self.scores[uid] = torch.FloatTensor([score])

        # Remove old records to free up memory
        for uid in list(self.rewards_log.keys()):
            self.rewards_log[uid] = [
                (r, t, qtype)
                for r, t, qtype in self.rewards_log[uid]
                if current_time - t <= 86400
            ]


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    updateAvailable = check_updates()
    if updateAvailable:
        bt.logging.info("Update available. Please update the validator.")
        print("Update available. Please update the validator.")
        exit(1)
    with Validator() as validator:
        while True:
            bt.logging.info(f"Validator running... {time.time()}")
            time.sleep(5)
