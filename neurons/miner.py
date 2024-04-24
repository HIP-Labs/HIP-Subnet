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
import os
import time
import typing
import bittensor as bt
from tinydb import TinyDB, where
from hip.version import check_updates
import hip

# import base miner class which takes care of most of the boilerplate
from hip.base.miner import BaseMinerNeuron


class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)
        print("Miner init", os.path.dirname(__file__))
        tasks_path = os.path.join(os.path.dirname(__file__), "../", "tasks_db.json")
        self.tasks_db = TinyDB(tasks_path)
        answers_path = os.path.join(os.path.dirname(__file__), "../", "answers_db.json")
        self.answers_db = TinyDB(answers_path)
        # Remove all the tasks and answers from the database
        # Because the miner is starting fresh
        # self.tasks_db.truncate()
        # self.answers_db.truncate()
        # TODO:(developer): Anything specific to your use case you can do here

    async def forward(
        self, synapse: hip.protocol.TaskSynapse
    ) -> hip.protocol.TaskSynapse:
        """
        Processes the incoming 'TaskSynapse' synapse by performing a predefined operation on the input data.

        Args:
            synapse (template.protocol.TaskSynapse): The synapse object containing the task data.

        Returns:
            template.protocol.TaskSynapse: The synapse object with the 'answer' field set to the answer from miner.
        """
        # TODO:(developer): Confim if the logic is correct
        print("Forwarding synapse")
        task = {
            "id": synapse.id,
            "label": synapse.label,
            "type": synapse.type,
            "options": synapse.options,
            "value": synapse.value,
            "image": synapse.image,
            "answer": "",
        }
        self.tasks_db.insert(task)
        start_time = time.time()
        timeout = 3 * 60  # 3 minutes
        answered = False
        # TODO: Commented out the timeout reconfigure it
        # if synapse.timeout:
        #     timeout = synapse.timeout
        while time.time() - start_time < timeout:
            if self.answers_db.search(where("id") == synapse.id):
                answered = True
                break
            time.sleep(1)
        if not answered:
            synapse.answer = "Not Answered"
            self.tasks_db.remove(where("id") == synapse.id)
            self.answers_db.remove(where("id") == synapse.id)
            return synapse
        answer = self.answers_db.search(where("id") == synapse.id)[0]
        synapse.answer = answer["answer"]
        self.answers_db.remove(where("id") == synapse.id)
        print(f"For the task: {synapse.id} the answer is: {synapse.answer}")
        return synapse

    # TODO: Check if the blacklist function is correct
    async def blacklist(
        self, synapse: hip.protocol.TaskSynapse
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (template.protocol.TaskSynapse): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """
        if not self.metagraph:
            bt.logging.warning(
                "Blacklist function called without metagraph. Blacklisting request."
            )
            return True, "No metagraph"
        if not synapse.dendrite or not synapse.dendrite.hotkey:
            bt.logging.warning(
                "Blacklist function called without synapse. Blacklisting request."
            )
            return True, "No hotkey"

        # TODO(developer): Define how miners should blacklist requests.
        uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
        if (
            not self.config.blacklist.allow_non_registered
            and synapse.dendrite.hotkey not in self.metagraph.hotkeys
        ):
            # Ignore requests from un-registered entities.
            bt.logging.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        if self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                bt.logging.warning(
                    f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
                )
                return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    # TODO: Check if the priority function is correct
    async def priority(self, synapse: hip.protocol.TaskSynapse) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (template.protocol.Dummy): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        if not self.metagraph:
            bt.logging.warning(
                "Priority function called without metagraph. Returning default priority of 0."
            )
            return 0

        if not synapse.dendrite or not synapse.dendrite.hotkey:
            bt.logging.warning(
                "Priority function called without synapse. Returning default priority of 0."
            )
            return 0

        # TODO(developer): Define how miners should prioritize requests.
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: {prirority}"
        )
        return prirority


# This is the main function, which runs the miner.
if __name__ == "__main__":
    bt.logging.info("Starting miner...")
    updateAvailable = check_updates()
    if updateAvailable:
        bt.logging.info("Update available. Please update the miner.")
        print("Update available. Please update the miner.")
        exit(1)
    with Miner() as miner:
        while True:
            bt.logging.info(f"Miner running... {time.time()}")
            time.sleep(5)
