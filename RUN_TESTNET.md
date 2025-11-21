# Running Miner on Testnet

## ✅ Code Status

Your miner is **READY** for testnet:
- ✅ `neurons/miner.py` - Modified to use `variation_generator_clean.py`
- ✅ `variation_generator_clean.py` - Uses simple algorithm (NO Ollama/Gemini)
- ✅ All dependencies in place

## 📋 Prerequisites

Before running, you need:

1. **Bittensor Wallet with Testnet TAO**
   - Create wallet if needed: `btcli wallet new_coldkey --wallet.name YOUR_WALLET`
   - Create hotkey: `btcli wallet new_hotkey --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY`
   - Get testnet TAO from faucet

2. **Register Miner on Subnet 54 (Testnet)**
   ```bash
   btcli subnet register \
     --netuid 54 \
     --wallet.name YOUR_WALLET \
     --wallet.hotkey YOUR_HOTKEY \
     --subtensor.network finney
   ```

3. **Network Setup**
   - Port 8091 must be open (for validator communication)
   - Ensure firewall allows inbound connections on port 8091

## 🚀 Run on Testnet

### Basic Command

```bash
python neurons/miner.py \
  --netuid 54 \
  --subtensor.network finney \
  --subtensor.chain_endpoint wss://entrypoint-finney.opentensor.ai:443 \
  --wallet.name YOUR_WALLET \
  --wallet.hotkey YOUR_HOTKEY \
  --logging.debug
```

### With Logging to File

```bash
python neurons/miner.py \
  --netuid 54 \
  --subtensor.network finney \
  --subtensor.chain_endpoint wss://entrypoint-finney.opentensor.ai:443 \
  --wallet.name YOUR_WALLET \
  --wallet.hotkey YOUR_HOTKEY \
  --logging.debug \
  > miner.log 2>&1
```

### Run in Background (Recommended)

```bash
# Using nohup
nohup python neurons/miner.py \
  --netuid 54 \
  --subtensor.network finney \
  --subtensor.chain_endpoint wss://entrypoint-finney.opentensor.ai:443 \
  --wallet.name YOUR_WALLET \
  --wallet.hotkey YOUR_HOTKEY \
  --logging.debug \
  > miner.log 2>&1 &

# Or using screen
screen -S miner
python neurons/miner.py \
  --netuid 54 \
  --subtensor.network finney \
  --subtensor.chain_endpoint wss://entrypoint-finney.opentensor.ai:443 \
  --wallet.name YOUR_WALLET \
  --wallet.hotkey YOUR_HOTKEY \
  --logging.debug

# Detach: Ctrl+A then D
# Reattach: screen -r miner
```

## 🔍 What Happens When Running

1. **Miner Starts**
   - Connects to Bittensor testnet (finney)
   - Registers on subnet 54
   - Opens port 8091 for validator connections
   - Logs: "MINER: Using variation_generator_clean.py (NO Ollama/Gemini)"

2. **Receives Request**
   - Validator sends `IdentitySynapse` via Bittensor
   - Miner validates request (whitelist check)
   - Routes to `variation_generator_clean.py`

3. **Generates Variations**
   - Uses simple algorithm (NO LLM)
   - Generates name, DOB, address variations
   - Returns format: `{name: [[name_var, dob_var, address_var], ...]}`

4. **Sends Response**
   - Returns `IdentitySynapse` with `variations` filled
   - Validator receives and scores

## ✅ Verify It's Working

Look for these log messages:
```
MINER: Using variation_generator_clean.py (NO Ollama/Gemini)
Verified call from Yanez (...)
Starting run {run_id} for N names
Generating variations using clean algorithm (no LLM)...
Request completed in X.XXs
```

## ⚠️ Troubleshooting

### Port Already in Use
```bash
# Check if port 8091 is in use
lsof -i :8091

# Or use different port
--axon.port 8092
```

### Wallet Not Found
```bash
# List wallets
btcli wallet list

# Check wallet balance
btcli wallet balance --wallet.name YOUR_WALLET --subtensor.network finney
```

### Not Registered
```bash
# Check registration status
btcli subnet show --netuid 54 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY --subtensor.network finney

# Register if needed
btcli subnet register --netuid 54 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY --subtensor.network finney
```

## 📝 Notes

- **NO Ollama/Gemini needed** - The miner now uses `variation_generator_clean.py`
- **Fast processing** - No LLM API latency
- **Testnet network**: `finney` (not mainnet)
- **Subnet**: 54

