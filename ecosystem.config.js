module.exports = {
  apps: [
    // Subtensor node
    // {
    //   name: "HIP_Subtensor",
    //   script: "/usr/local/bin/node-subtensor",
    //   args: "--chain /subtensor/raw_testspec.json --base-path /tmp/blockchain --sync=warp --execution wasm --wasm-execution compiled --port 30333 --max-runtime-instances 64 --rpc-max-response-size 2048 --rpc-cors all --rpc-port 9933 --ws-port 9944 --bootnodes /dns/bootnode.test.finney.opentensor.ai/tcp/30333/p2p/12D3KooWPM4mLcKJGtyVtkggqdG84zWrd7Rij6PGQDoijh1X86Vr --ws-max-connections 16000 --no-mdns --in-peers 8000 --out-peers 8000 --prometheus-external --rpc-external --ws-external",
    //   exec_interpreter: "none",
    //   autorestart: true,
    //   watch: false,
    //   max_memory_restart: "2G",
    // },
    // HIP Miner
    {
      name: "miner",
      script: "./neurons/miner.py",
      interpreter: "/home/ubuntu/HIP-Subnet/venv/bin/python",
      autorestart: true,
    },
    // HIP Miner Frontend
    {
      name: "frontend",
      script: "uvicorn",
      args: "frontend:app --port 3001",
      autorestart: true,
    },
  ],
};
