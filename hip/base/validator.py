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


from collections import defaultdict
import copy
import torch
import asyncio
import argparse
import threading
import bittensor as bt
from typing import List, Literal
from traceback import print_exception

from hip.base.neuron import BaseNeuron
from hip.mock import MockDendrite
from hip.utils.config import add_validator_args
from hip.utils.misc import get_utc_timestamp
from hip.validator.reward import linear_rewards


class BaseValidatorNeuron(BaseNeuron):
    """
    Base class for Bittensor validators. Your validator should inherit from this class.
    """

    neuron_type: str = "ValidatorNeuron"

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        super().add_args(parser)
        add_validator_args(cls, parser)

    def __init__(self, config=None):
        super().__init__(config=config)

        # Save a copy of the hotkeys to local memory.
        self.hotkeys = copy.deepcopy(self.metagraph.hotkeys)

        self.dendrite = bt.dendrite(wallet=self.wallet)
        bt.logging.info(f"Dendrite: {self.dendrite}")

        # Set up initial scoring weights for validation
        bt.logging.info("self.score: Building validation weights.")
        self.scores = torch.zeros(
            self.metagraph.n, dtype=torch.float32, device=self.device  # type: ignore
        )  # type: ignore
        # tasks_history is a list of lists, where each list contains tuples of the form (is_answer_correct: bool, timestamp: int, question_type: Literal["captcha", "normal"]) for each question answered by a miner.
        # the base list is indexed by the miner's uid. len(self.metagraph.uids) is the length of the list.
        self.tasks_history: list[
            list[tuple[bool, int, Literal["captcha", "normal"]]]
        ] = [[] for _ in range(self.metagraph.n)]
        # Init sync with the network. Updates the metagraph.
        self.sync()

        # Serve axon to enable external connections.
        if not self.config.neuron.axon_off:
            self.serve_axon()
        else:
            bt.logging.warning("axon off, not serving ip to chain.")

        # Create asyncio event loop to manage async tasks.
        self.loop = asyncio.get_event_loop()

        # Instantiate runners
        self.should_exit: bool = False
        self.is_running: bool = False
        self.thread: threading.Thread = None  # type: ignore
        self.lock = asyncio.Lock()

    def serve_axon(self):
        """Serve axon to enable external connections."""

        bt.logging.info("serving ip to chain...")
        try:
            self.axon = bt.axon(wallet=self.wallet, config=self.config)  # type: ignore

            try:
                self.subtensor.serve_axon(
                    netuid=self.config.netuid,
                    axon=self.axon,
                )
                bt.logging.info(
                    f"Running validator {self.axon} on network: {self.config.subtensor.chain_endpoint} with netuid: {self.config.netuid}"
                )
            except Exception as e:
                bt.logging.error(f"Failed to serve Axon with exception: {e}")
                pass

        except Exception as e:
            bt.logging.error(f"Failed to create Axon initialize with exception: {e}")
            pass

    async def concurrent_forward(self):
        coroutines = [
            self.forward() for _ in range(self.config.neuron.num_concurrent_forwards)  # type: ignore
        ]
        await asyncio.gather(*coroutines)

    def run(self):
        """
        Initiates and manages the main loop for the miner on the Bittensor network. The main loop handles graceful shutdown on keyboard interrupts and logs unforeseen errors.

        This function performs the following primary tasks:
        1. Check for registration on the Bittensor network.
        2. Continuously forwards queries to the miners on the network, rewarding their responses and updating the scores accordingly.
        3. Periodically resynchronizes with the chain; updating the metagraph with the latest network state and setting weights.

        The essence of the validator's operations is in the forward function, which is called every step. The forward function is responsible for querying the network and scoring the responses.

        Note:
            - The function leverages the global configurations set during the initialization of the miner.
            - The miner's axon serves as its interface to the Bittensor network, handling incoming and outgoing requests.

        Raises:
            KeyboardInterrupt: If the miner is stopped by a manual interruption.
            Exception: For unforeseen errors during the miner's operation, which are logged for diagnosis.
        """

        # Check that validator is registered on the network.
        self.sync()

        if not self.config.neuron.axon_off:
            bt.logging.info(
                f"Running validator {self.axon} on network: {self.config.subtensor.chain_endpoint} with netuid: {self.config.netuid}"
            )
        else:
            bt.logging.info(
                f"Running validator on network: {self.config.subtensor.chain_endpoint} with netuid: {self.config.netuid}"
            )

        bt.logging.info(f"Validator starting at block: {self.block}")

        # This loop maintains the validator's operations until intentionally stopped.
        try:
            while True:
                bt.logging.info(f"step({self.step}) block({self.block})")

                # Run multiple forwards concurrently.
                self.loop.run_until_complete(self.concurrent_forward())

                # Check if we should exit.
                if self.should_exit:
                    break

                # Sync metagraph and potentially set weights.
                self.sync()

                self.step += 1

        # If someone intentionally stops the validator, it'll safely terminate operations.
        except KeyboardInterrupt:
            self.axon.stop()
            bt.logging.success("Validator killed by keyboard interrupt.")
            exit()

        # In case of unforeseen errors, the validator will log the error and continue operations.
        except Exception as err:
            bt.logging.error("Error during validation", str(err))
            bt.logging.debug(print_exception(type(err), err, err.__traceback__))  # type: ignore

    def run_in_background_thread(self):
        """
        Starts the validator's operations in a background thread upon entering the context.
        This method facilitates the use of the validator in a 'with' statement.
        """
        if not self.is_running:
            bt.logging.debug("Starting validator in background thread.")
            self.should_exit = False
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.is_running = True
            bt.logging.debug("Started")

    def stop_run_thread(self):
        """
        Stops the validator's operations that are running in the background thread.
        """
        if self.is_running:
            bt.logging.debug("Stopping validator in background thread.")
            self.should_exit = True
            self.thread.join(5)
            self.is_running = False
            bt.logging.debug("Stopped")

    def __enter__(self):
        self.run_in_background_thread()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the validator's background operations upon exiting the context.
        This method facilitates the use of the validator in a 'with' statement.

        Args:
            exc_type: The type of the exception that caused the context to be exited.
                      None if the context was exited without an exception.
            exc_value: The instance of the exception that caused the context to be exited.
                       None if the context was exited without an exception.
            traceback: A traceback object encoding the stack trace.
                       None if the context was exited without an exception.
        """
        if self.is_running:
            bt.logging.debug("Stopping validator in background thread.")
            self.should_exit = True
            self.thread.join(5)
            self.is_running = False
            bt.logging.debug("Stopped")

    def set_weights(self):
        print("set_weights called")
        """
        Sets the validator weights to the metagraph hotkeys based on the scores it has received from the miners. The weights determine the trust and incentive level the validator assigns to miner nodes on the network.
        """

        # Check if self.scores contains any NaN values and log a warning if it does.
        if torch.isnan(self.scores).any():
            bt.logging.warning(
                f"self.score: Scores contain NaN values. This may be due to a lack of responses from miners, or a bug in your reward functions."
            )

        bt.logging.debug("Setting weights on chain with scores: ")
        bt.logging.debug(self.scores)
        # Calculate the average reward for each uid across non-zero values.
        # Replace any NaN values with 0.
        raw_weights = torch.nn.functional.normalize(self.scores, p=1, dim=0)

        bt.logging.debug("raw_weights", raw_weights)  # type: ignore
        bt.logging.debug("raw_weight_uids", self.metagraph.uids.to("cpu"))  # type: ignore
        # Process the raw weights to final_weights via subtensor limitations.
        (
            processed_weight_uids,
            processed_weights,
        ) = bt.utils.weight_utils.process_weights_for_netuid(  # type: ignore
            uids=self.metagraph.uids.to("cpu"),
            weights=raw_weights.to("cpu"),
            netuid=self.config.netuid,
            subtensor=self.subtensor,
            metagraph=self.metagraph,
        )
        bt.logging.debug("processed_weights", processed_weights)
        bt.logging.debug("processed_weight_uids", processed_weight_uids)

        # Convert to uint16 weights and uids.
        (
            uint_uids,
            uint_weights,
        ) = bt.utils.weight_utils.convert_weights_and_uids_for_emit(  # type: ignore
            uids=processed_weight_uids, weights=processed_weights  # type: ignore
        )
        bt.logging.debug("uint_weights", uint_weights)
        bt.logging.debug("uint_uids", uint_uids)
        # Set the weights on chain via our subtensor connection.
        result, msg = self.subtensor.set_weights(
            wallet=self.wallet,
            netuid=self.config.netuid,
            uids=uint_uids,
            weights=uint_weights,
            wait_for_finalization=False,
            wait_for_inclusion=False,
            version_key=self.spec_version,
        )
        if result is True:
            bt.logging.info("set_weights on chain successfully!")
        else:
            bt.logging.error("set_weights failed", msg)

    def resync_metagraph(self):
        print("resync_metagraph called")
        """Resyncs the metagraph and updates the hotkeys based on the new metagraph."""
        bt.logging.info("resync_metagraph()")

        # Copies state of metagraph before syncing.
        previous_metagraph = copy.deepcopy(self.metagraph)

        # Sync the metagraph.
        self.metagraph.sync(subtensor=self.subtensor)

        # Check if the metagraph axon info has changed.
        if previous_metagraph.axons == self.metagraph.axons:
            return

        bt.logging.info(
            "Metagraph updated, re-syncing hotkeys, dendrite pool and scores"
        )
        # Zero out all hotkeys that have been replaced.
        for uid, hotkey in enumerate(self.hotkeys):
            if hotkey != self.metagraph.hotkeys[uid]:
                bt.logging.debug(f"Hotkey {hotkey} has been replaced.")
                bt.logging.debug(f"self.score: Zeroing out score for uid {uid}")
                self.scores[uid] = 0  # hotkey has been replaced
                self.tasks_history[uid] = []  # clear rewards log

        # Check to see if the metagraph has changed size.
        # If so, we need to add new hotkeys and scores.
        if len(self.hotkeys) < len(self.metagraph.hotkeys):
            # TODO: Implement this. For now, we just reset the scores.
            bt.logging.warning(
                "self.score: Metagraph has grown in size. Resetting scores and hotkeys."
            )
            # Update the size of the scores.
            all_scores = torch.zeros((self.metagraph.n)).to(self.device)  # type: ignore
            min_len = min(len(self.hotkeys), len(self.scores))
            all_scores[:min_len] = self.scores[:min_len]
            self.scores = all_scores
            # Update the size of the tasks_history.
            all_tasks_history: list[
                list[tuple[bool, int, Literal["captcha", "normal"]]]
            ] = [[] for _ in range(self.metagraph.n)]
            min_len = min(len(self.tasks_history), len(all_tasks_history))
            all_tasks_history[:min_len] = self.tasks_history[:min_len]
            self.tasks_history = all_tasks_history
        # Update the hotkeys.
        self.hotkeys = copy.deepcopy(self.metagraph.hotkeys)

    def update_scores(
        self,
        is_correct_answers: List[bool],
        uids: List[int],
        question_type: Literal["captcha", "normal"],
    ):
        current_time = get_utc_timestamp()
        bt.logging.info(f"Updating scores called with rewards")
        bt.logging.debug(f"uids: {uids}")
        bt.logging.debug(f"is_correct_answers: {is_correct_answers}")
        bt.logging.debug(f"question_type: {question_type}")
        bt.logging.debug(f"current_time: {current_time}")
        bt.logging.debug(self.tasks_history)
        bt.logging.debug(self.scores)
        for uid, is_answer_correct in zip(uids, is_correct_answers):
            if uid not in self.tasks_history:
                self.tasks_history[uid] = []
            self.tasks_history[uid].append(
                (is_answer_correct, current_time, question_type)
            )

        # Now that we have the rewards, we can update the scores.

        for uid in uids:
            recent_tasks = self.tasks_history[uid]
            # remove old records
            recent_tasks = [
                (is_answer_correct, task_time, question_type)
                for is_answer_correct, task_time, question_type in recent_tasks
                if current_time - task_time < 86400
            ]
            # Separate regular questions and captchas
            correct_answers = sum(
                1
                for is_answer_correct, task_time, question_type in recent_tasks
                if is_answer_correct == True
            )
            correct_capthas = sum(
                1
                for is_answer_correct, task_time, question_type in recent_tasks
                if is_answer_correct == True and question_type == "captcha"
            )

            captcha_penalties = sum(
                1
                for is_answer_correct, task_time, question_type in recent_tasks
                if question_type == "captcha" and is_answer_correct == False
            )
            wrong_answers = sum(
                1
                for is_answer_correct, task_time, question_type in recent_tasks
                if is_answer_correct == False and question_type != "captcha"
            )
            score = linear_rewards(self, correct_answers)

            penalize_score = True
            # Realistically, a real human being can't answer for more than 4 hours in a day
            # so we do not penalize the score if the miner has answered more than 4 hours in a day
            # We know that probability of a captcha occuring is 10% in whole day we will get
            # 10% of 480 = 48 captchas in a day
            # in 4 hours we will get 8 captchas ((4 * 60) / 3)* 0.1 = 8
            if correct_capthas > 8:
                penalize_score = False

            if penalize_score:
                # For each wrong answer, penalize the score by 1% by computing the penalty
                # as 1% of the total number of wrong answers
                for i in range(wrong_answers):
                    score = score * 0.99

                # For each wrong captcha answer, penalize the score by 5% by computing the penalty
                # as 5% of the total number of failed captchas
                for i in range(captcha_penalties):
                    score = score * 0.95

            bt.logging.debug(
                f"self.score: Updating score for miner {uid} with score {score}"
            )
            # Update the scores tensor
            self.scores[uid] = torch.FloatTensor([score])

        # Remove old records to free up memory
        for i in range(len(self.tasks_history)):
            for t in self.tasks_history[i]:
                if current_time - t[1] > 86400:
                    self.tasks_history[i].remove(t)

    def save_state(self):
        """Saves the state of the validator to a file."""
        bt.logging.info("Saving validator state.")
        bt.logging.debug(f"self.score: Saved step {self.step} in state.")

        # Save the state of the validator to file.
        torch.save(
            {
                "step": self.step,
                "scores": self.scores,
                "hotkeys": self.hotkeys,
                "tasks_history": self.tasks_history,
            },
            self.config.neuron.full_path + "/state.pt",
        )

    def load_state(self):
        """Loads the state of the validator from a file."""
        bt.logging.info("Loading validator state.")

        # Load the state of the validator from file.
        state = torch.load(self.config.neuron.full_path + "/state.pt")
        self.step = state["step"]
        bt.logging.debug(f"self.score: Loaded step {self.step} from state.")
        self.scores = state["scores"]
        self.hotkeys = state["hotkeys"]
        self.tasks_history = state["tasks_history"]
