import os
import requests


def get_version():
    with open("VERSION", "r") as version_file:
        __version__ = version_file.read().strip()
    return __version__


def generate_spec_version(version: str):
    version_split = version.split(".")
    return (
        (10000 * int(version_split[0]))
        + (100 * int(version_split[1]))
        + (1 * int(version_split[2]))
    )


async def check_updates() -> bool:
    url = "https://raw.githubusercontent.com/HIP-Labs/HIP-Subnet/main/VERSION"
    response = requests.get(url)
    latest_version = response.text.strip()
    latest_version_spec = generate_spec_version(latest_version)
    current_version = get_version()
    current_version_spec = generate_spec_version(current_version)
    print(f"Latest version: {latest_version}")
    print(f"Current version: {current_version}")
    if latest_version_spec > current_version_spec:
        print(f"New version available: {latest_version}")
        return True
    else:
        print(f"Running latest version: {current_version}")
        return False
