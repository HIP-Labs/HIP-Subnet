import aiohttp
from hip.protocol import TaskSynapse
from hip.constants import HIP_SERVICE_URL


# TODO: Call the HIP Service api to get the task
async def get_task() -> TaskSynapse:
    # send a GET request to the HIP_SERVICE_URL and create a TaskSynapse object
    async with aiohttp.ClientSession() as session:
        async with session.get(HIP_SERVICE_URL) as response:
            response_data = await response.json()
            return TaskSynapse(
                id=response_data["id"],
                label=response_data["label"],
                type=response_data["type"],
                options=response_data["options"],
                value=response_data["value"],
                image=response_data["image"],
                answer="",
            )
