#!/bin/bash
# Command to run miner on testnet

python neurons/miner.py \
  --netuid 322 \
  --subtensor.network test \
  --subtensor.chain_endpoint wss://test.finney.opentensor.ai:443 \
  --wallet.name abc \
  --wallet.hotkey abc \
  --logging.debug

