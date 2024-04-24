#!/bin/bash

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a package is installed
is_installed() {
    dpkg -s "$1" >/dev/null 2>&1
}

# Print HIP ASCII art and description
clear
echo -e "${YELLOW}"
cat << "EOF"

██╗  ██╗██╗██████╗     ███████╗██╗   ██╗██████╗ ███╗   ██╗███████╗████████╗
██║  ██║██║██╔══██╗    ██╔════╝██║   ██║██╔══██╗████╗  ██║██╔════╝╚══██╔══╝
███████║██║██████╔╝    ███████╗██║   ██║██████╔╝██╔██╗ ██║█████╗     ██║   
██╔══██║██║██╔═══╝     ╚════██║██║   ██║██╔══██╗██║╚██╗██║██╔══╝     ██║   
██║  ██║██║██║         ███████║╚██████╔╝██████╔╝██║ ╚████║███████╗   ██║   
╚═╝  ╚═╝╚═╝╚═╝         ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝  
       
EOF
echo -e "${NC}"
echo "The HIP (Human Intelligence Primitive) Subnet is a Bittensor subnet designed to provide human intelligence services to other subnets. It allows other subnets to send their data to the HIP Subnet for human evaluation, testing, and feedback."
echo
read -p "Press Enter to continue the installation or any other key to abort..." -n1 -s
echo

# Check if the script was aborted
if [ $? -ne 0 ]; then
    echo -e "${RED}Installation aborted.${NC}"
    exit 1
fi

# Update package list
echo -e "${GREEN}Updating package list...${NC}"
sudo apt-get update

# Check if python3.10-venv is installed, and install it if not
if ! is_installed "python3.10-venv"; then
    echo -e "${GREEN}Installing python3.10-venv...${NC}"
    sudo apt-get install -y python3.10-venv
fi

# Create a virtual environment and activate it
echo -e "${GREEN}Creating and activating virtual environment...${NC}"
python3 -m venv env
source env/bin/activate

# Install the required dependencies
echo -e "${GREEN}Installing required dependencies...${NC}"
python3 -m pip install -e .

# Print progress bar
echo -e "${GREEN}Installation progress:${NC}"
for ((i=0; i<=100; i+=5)); do
    sleep 0.1
    progress=$((i*40/100))
    printf "\r[%-40s] %3d%%" "${YELLOW}$(printf '#%.0s' $(seq 1 $progress))${NC}" "$i"
done
echo

# Print installation success message
echo -e "${GREEN}HIP Subnet installation completed successfully!${NC}"
