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
import pydantic
from typing import List, AsyncIterator
import pdb


class TaskSynapse(bt.Synapse):
    """
    The TaskSynapse subclass of the Synapse class encapsulates the functionalities related to HIP Task Scenerios.

    It specifies seven fields - `id`, `label`, `type`, `options`, `value`, `image`, `answer` - that define the state of the TaskSynapse object.
    All of the fields except `answer` are read-only fields defined during object initialization, and `answer` is a mutable
    field that can be updated as the scenario progresses.

    The Config inner class specifies that assignment validation should occur on this class (validate_assignment = True),
    meaning value assignments to the instance fields are checked against their defined types for correctness.

    Attributes:
        id (str): A unique identifier for the task. This field is both mandatory and immutable.
        label (str): A string that describes the task. This field is both mandatory and immutable.
        type (str): A string that specifies the type of the task. This field is both mandatory and immutable.
        options (List[str]): A list of options for the task. This field is both mandatory and immutable.
        value (str): A string that captures the value of the task. This field is both mandatory and immutable.
        image (str): A string that captures the image of the task. This field is both mandatory and immutable.
        answer (str): A string that captures the answer to the task. This field is mutable.
        required_hash_fields List[str]: A list of fields that are required for the hash.

    Methods:
        deserialize() -> "TaskSynapse": Returns the instance of the current object.


    The `TaskSynapse` class also overrides the `deserialize` method, returning the
    instance itself when this method is invoked. Additionally, it provides a `Config`
    inner class that enforces the validation of assignments (`validate_assignment = True`).

    Here is an example of how the `TaskSynapse` class can be used:

    ```python
    # Create a TaskSynapse instance
    task = TaskSynapse(
        id="1",
        label="What is the meaning of life?",
        type="select",
        options=["42", "24", "100", "0"],
        value="The life in its entirety is a mystery. But the meaning of life is 42. Deal with it, human.",
        image="https://example.com/image.jpg",
    )

    # Print the roles and messages
    print("Options:", task.options)
    print("Label:", task.label)

    # Take input for the answer from user
    if task.type == "select": # select from options
        option = input("Select the correct option: ")
        answer = task.options[int(option)]
    else: # input the answer
        task.answer = input("Enter the answer: ")

    # Print the answer
    print("Answer:", task.answer)
    ```

    This will output:
    ```
    Options: ['42', '24', '100', '0']
    Label: What is the meaning of life?
    Select the correct option: 0
    Answer: 42
    ```

    This example demonstrates how to create an instance of the `TaskSynapse` class, access the
    `options` and `label` fields, and update the `answer` field.
    """

    class Config:
        """
        Pydantic model configuration class for TaskSynapse. This class sets validation of attribute assignment as True.
        validate_assignment set to True means the pydantic model will validate attribute assignments on the class.
        """

        validate_assignment = True

    def deserialize(self) -> "TaskSynapse":
        """
        Returns the instance of the current TaskSynapse object.

        This method is intended to be potentially overridden by subclasses for custom deserialization logic.
        In the context of the TaskSynapse class, it simply returns the instance itself. However, for subclasses
        inheriting from this class, it might give a custom implementation for deserialization if need be.

        Returns:
            TaskSynapse: The current instance of the TaskSynapse class.
        """
        return self

    id: str = pydantic.Field(
        ...,
        title="ID",
        description="A unique identifier for the task.",
        allow_mutation=False,
    )

    label: str = pydantic.Field(
        ...,
        title="Label",
        description="A string that describes the task.",
        allow_mutation=False,
    )

    type: str = pydantic.Field(
        ...,
        title="Type",
        description="A string that specifies the type of the task.",
        allow_mutation=False,
    )

    options: List[str] = pydantic.Field(
        ...,
        title="Options",
        description="A list of options for the task.",
        allow_mutation=False,
    )

    value: str = pydantic.Field(
        ...,
        title="Value",
        description="A string that captures the value of the task.",
        allow_mutation=False,
    )

    captcha: str = pydantic.Field(
        ...,
        title="Captcha",
        description="A base64 image string of the captcha image.",
        allow_mutation=False,
    )

    image: str = pydantic.Field(
        ...,
        title="Image",
        description="A string that captures the image of the task.",
        allow_mutation=False,
    )

    answer: str = pydantic.Field(
        "",
        title="Answer",
        description="A string that captures the answer to the task.",
    )

    captchaValue: str = pydantic.Field(
        "",
        title="Captcha Value",
        description="The value of the captcha.",
    )

    #  required_hash_fields is the list of fields that are required for the hash for the request body.
    required_hash_fields: List[str] = pydantic.Field(
        ["id", "label", "type", "options", "value", "image", "captcha"],
        title="Required Hash Fields",
        description="A list of fields that are required for the hash.",
        allow_mutation=False,
    )

    def __str__(self) -> str:
        """
        Returns a string representation of the TaskSynapse object.

        Returns:
            str: A string representation of the TaskSynapse object.
        """
        return f"TaskSynapse(id={self.id}, label={self.label}, type={self.type}, options={self.options}, value={self.value}, image={self.image}, answer={self.answer}, captchaValue={self.captchaValue}, captcha={self.captcha}, required_hash_fields={self.required_hash_fields})"

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "type": self.type,
            "options": self.options,
            "value": self.value,
            "image": self.image,
            "answer": self.answer,
            "captchaValue": self.captchaValue,
            "captcha": self.captcha,
            "required_hash_fields": self.required_hash_fields,
        }
