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


def check_updates() -> bool:
    url = "https://raw.githubusercontent.com/HIP-Labs/HIP-Subnet/main/VERSION"
    response = requests.get(url)
    latest_version = response.text.strip()
    latest_version_spec = generate_spec_version(latest_version)
    current_version = get_version()
    current_version_spec = generate_spec_version(current_version)
    print(f"Latest version: {latest_version}")
    print(f"Current version: {current_version}")
    # check if the latest version is greater than the current version
    # Only check the major and minor version numbers not the patch version
    if latest_version_spec // 100 > current_version_spec // 100:
        return True
    else:
        return False
