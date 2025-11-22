# Running Miner on Mainnet with Gemini

## 🚀 Quick Start Command

### Basic Command (with Gemini)

```bash
export GEMINI_API_KEY=AIzaSyDsCTkdmpb_XIl80NiDX3mr-7l9Ke3qJrA

python neurons/miner.py \
  --netuid 54 \
  --subtensor.network archive \
  --wallet.name YOUR_WALLET \
  --wallet.hotkey YOUR_HOTKEY \
  --neuron.gemini_api_key $GEMINI_API_KEY \
  --neuron.gemini_model gemini-2.0-flash-exp \
  --logging.debug
```

### Run in Background (Recommended)

```bash
export GEMINI_API_KEY=AIzaSyDsCTkdmpb_XIl80NiDX3mr-7l9Ke3qJrA

nohup python neurons/miner.py \
  --netuid 54 \
  --subtensor.network archive \
  --wallet.name YOUR_WALLET \
  --wallet.hotkey YOUR_HOTKEY \
  --neuron.gemini_api_key $GEMINI_API_KEY \
  --neuron.gemini_model gemini-2.0-flash-exp \
  --logging.debug \
  > miner_mainnet.log 2>&1 &

# Check if running
tail -f miner_mainnet.log
```

### Using Screen (Alternative)

```bash
export GEMINI_API_KEY=AIzaSyDsCTkdmpb_XIl80NiDX3mr-7l9Ke3qJrA

screen -S miner_mainnet

python neurons/miner.py \
  --netuid 54 \
  --subtensor.network archive \
  --wallet.name YOUR_WALLET \
  --wallet.hotkey YOUR_HOTKEY \
  --neuron.gemini_api_key $GEMINI_API_KEY \
  --neuron.gemini_model gemini-2.0-flash-exp \
  --logging.debug

# Detach: Ctrl+A then D
# Reattach: screen -r miner_mainnet
```

## 📋 Prerequisites

1. **Bittensor Wallet with Mainnet TAO**
   ```bash
   # Check wallet balance
   btcli wallet balance --wallet.name YOUR_WALLET --subtensor.network archive
   ```

2. **Register Miner on Subnet 54 (Mainnet)**
   ```bash
   btcli subnet register \
     --netuid 54 \
     --wallet.name YOUR_WALLET \
     --wallet.hotkey YOUR_HOTKEY \
     --subtensor.network archive
   ```

3. **Gemini API Key**
   - Set as environment variable: `export GEMINI_API_KEY=your_key`
   - Or pass via config: `--neuron.gemini_api_key your_key`

4. **Port 8091 Open**
   - Ensure firewall allows inbound connections on port 8091

## 🔧 Configuration Options

### Gemini Configuration

```bash
# Use Gemini (recommended for maximum scores)
--neuron.gemini_api_key YOUR_API_KEY
--neuron.gemini_model gemini-2.0-flash-exp  # or gemini-1.5-pro, etc.

# Or set via environment variable
export GEMINI_API_KEY=YOUR_API_KEY
```

### Network Configuration

```bash
# Mainnet (default)
--subtensor.network archive

# Custom chain endpoint (if needed)
--subtensor.chain_endpoint wss://entrypoint-finney.opentensor.ai:443
```

### Port Configuration

```bash
# Default port 8091
--axon.port 8091

# Custom port
--axon.port 8092
```

## ✅ Verify It's Working

Look for these log messages:
```
MINER: Using Gemini generator (Model: gemini-2.0-flash-exp)
Verified call from Yanez (...)
Starting run {run_id} for N names
Routing request to Gemini generator
Generation complete
Request completed in X.XXs
```

## ⚠️ Important Notes

1. **Gemini API Costs**: Monitor your API usage and costs
2. **Rate Limits**: Gemini has rate limits - monitor for errors
3. **Fallback**: If Gemini fails, miner falls back to `variation_generator_clean.py`
4. **Mainnet TAO**: Ensure you have sufficient TAO for registration and operations

## 🔍 Troubleshooting

### Check Registration Status
```bash
btcli subnet show \
  --netuid 54 \
  --wallet.name YOUR_WALLET \
  --wallet.hotkey YOUR_HOTKEY \
  --subtensor.network archive
```

### Check Wallet Balance
```bash
btcli wallet balance \
  --wallet.name YOUR_WALLET \
  --subtensor.network archive
```

### Check if Port is Open
```bash
# Check if port 8091 is in use
lsof -i :8091

# Or test from another machine
telnet YOUR_IP 8091
```

### View Logs
```bash
# If running with nohup
tail -f miner_mainnet.log

# If running in screen
screen -r miner_mainnet
```

## 📊 Expected Behavior

1. **Miner Starts**
   - Connects to Bittensor mainnet (archive)
   - Registers on subnet 54
   - Opens port 8091 for validator connections
   - Logs: "MINER: Using Gemini generator"

2. **Receives Request**
   - Validator sends `IdentitySynapse` via Bittensor
   - Miner validates request (whitelist check)
   - Routes to Gemini generator

3. **Generates Variations**
   - Uses Gemini API to generate optimal variations
   - Applies all scoring criteria (similarity, rules, etc.)
   - Returns format: `{name: [[name_var, dob_var, address_var], ...]}`

4. **Sends Response**
   - Returns `IdentitySynapse` with `variations` filled
   - Validator receives and scores

## 🎯 Performance Expectations

With Gemini integration:
- **Similarity Score**: Should improve with better prompt
- **Rule Compliance**: Should be applied correctly
- **Address Quality**: Excellent (0.9-1.0 API scores)
- **DOB Categories**: Perfect (all 6 categories)
- **Overall Score**: Target 0.65-0.80 (depending on similarity matching)

