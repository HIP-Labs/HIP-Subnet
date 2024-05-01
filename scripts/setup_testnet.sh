echo "Setting up Subtensor Testnet" &&
    cd ~ &&
    sudo apt update &&
    echo "Installing dependencies" &&
    sudo apt install -y make build-essential git clang curl libssl-dev llvm libudev-dev protobuf-compiler tmux  > /dev/null 2>&1 &&
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash &&
    source ~/.nvm/nvm.sh &&
    nvm install --lts &&
    npm install -g pm2 &&
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y &&
    source "$HOME/.cargo/env" &&
    git clone https://github.com/opentensor/subtensor.git &&
    chmod +x ./subtensor/scripts/init.sh &&
    ./subtensor/scripts/init.sh &&
    cd subtensor &&
    cargo build --release --features=runtime-benchmarks &&
    # This next command will run the node so it should be run in the background using pm2
    pm2 start ./target/release/node-subtensor --name HIP_Subtensor -- --chain raw_testspec.json --base-path /tmp/blockchain --sync=warp --execution wasm --wasm-execution compiled --port 30333 --max-runtime-instances 64 --rpc-max-response-size 2048 --rpc-cors all --rpc-port 9933 --ws-port 9944 --bootnodes /dns/bootnode.test.finney.opentensor.ai/tcp/30333/p2p/12D3KooWPM4mLcKJGtyVtkggqdG84zWrd7Rij6PGQDoijh1X86Vr --ws-max-connections 16000 --no-mdns --in-peers 8000 --out-peers 8000 --prometheus-external --rpc-external --ws-external &&
    cd ~ &&
    git clone https://github.com/HIP-Labs/HIP-Subnet &&
    cd HIP-Subnet &&
    pm2 del HIP_Miner &&
    pm2 start ./scripts/run_miner.sh --name HIP_Miner &&
    pm2 start ./scripts/run_miner_frontend.sh --name HIP_Miner_Frontend &&
    pm2 save &&
    echo "Subtensor Testnet setup complete" &&
    echo "Subtensor Testnet is running in the background" &&
    echo "To view the logs, run 'pm2 logs'"
