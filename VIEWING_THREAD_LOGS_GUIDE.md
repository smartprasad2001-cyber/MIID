# Guide: Viewing Thread Logs in Real-Time

## Overview

The address cache generation script now includes **color-coded, thread-identified logging** that makes it easy to see what all 8 threads are doing simultaneously.

---

## Log Format

Each log line follows this format:

```
[HH:MM:SS.mmm] [Thread-ID] message
```

**Example:**
```
[14:23:45.123] [Thread- 1] 📍 City 1/200: New York (40.7128, -74.0060)
[14:23:45.234] [Thread- 2] 📍 City 2/200: Los Angeles (34.0522, -118.2437)
[14:23:46.123] [Thread- 1] ✅ ACCEPTED (score: 1.0000 [1.0], total: 1/15): 123 Main St...
```

### Color Coding

- **Main Thread**: Bold Cyan
- **Thread 1**: Blue
- **Thread 2**: Green
- **Thread 3**: Yellow
- **Thread 4**: Magenta
- **Thread 5**: Cyan
- **Thread 6**: Red
- **Thread 7**: White
- **Thread 8**: Dark Gray

---

## Viewing Methods

### Method 1: Direct Terminal Output (Colored)

Simply run the script and watch the colored output:

```bash
python3 generate_address_cache.py
```

**Pros:**
- See colors in real-time
- Immediate feedback
- Easy to distinguish threads

**Cons:**
- Can't scroll back
- Hard to filter

---

### Method 2: Save to File and View in Real-Time

Save logs to a file while viewing them:

```bash
python3 generate_address_cache.py 2>&1 | tee address_cache.log
```

**In another terminal, view in real-time:**
```bash
tail -f address_cache.log
```

**Pros:**
- Can scroll back in the file
- Can view in another terminal
- Preserves all logs

**Cons:**
- Colors may not show in `tail`

---

### Method 3: View with Colors Preserved

Save logs and view with color support:

```bash
# Save logs
python3 generate_address_cache.py 2>&1 | tee address_cache.log

# View with colors (in another terminal)
tail -f address_cache.log | less -R
```

**Or use `multitail` (if installed):**
```bash
multitail address_cache.log
```

**Pros:**
- Colors preserved
- Can scroll back
- Better for analysis

---

### Method 4: Filter by Specific Thread

View logs from a specific thread only:

```bash
# View only Thread 1
tail -f address_cache.log | grep "Thread- 1"

# View only Thread 2
tail -f address_cache.log | grep "Thread- 2"

# View only Main Thread
tail -f address_cache.log | grep "MainThread"
```

**Or use multiple terminals:**
```bash
# Terminal 1: Thread 1
tail -f address_cache.log | grep --color=always "Thread- 1"

# Terminal 2: Thread 2
tail -f address_cache.log | grep --color=always "Thread- 2"

# Terminal 3: Thread 3
tail -f address_cache.log | grep --color=always "Thread- 3"
```

---

### Method 5: View All Threads Side-by-Side

Use `tmux` or `screen` to split terminal:

```bash
# Start tmux
tmux

# Split into 4 panes (Ctrl+B, then % for vertical, " for horizontal)
# In each pane, filter by different thread:
tail -f address_cache.log | grep "Thread- 1"
tail -f address_cache.log | grep "Thread- 2"
tail -f address_cache.log | grep "Thread- 3"
tail -f address_cache.log | grep "Thread- 4"
```

---

### Method 6: Use `multitail` for Multiple Threads

Install `multitail` (if not installed):
```bash
# macOS
brew install multitail

# Linux
sudo apt-get install multitail
```

Use it to view multiple filtered views:
```bash
multitail -s 2 \
  -l "grep 'Thread- 1' address_cache.log" \
  -l "grep 'Thread- 2' address_cache.log" \
  -l "grep 'Thread- 3' address_cache.log" \
  -l "grep 'Thread- 4' address_cache.log"
```

---

## Log Message Types

### City Processing Start
```
[14:23:45.123] [Thread- 1] 📍 City 1/200: New York (40.7128, -74.0060)
```

### Nodes Fetched
```
[14:23:45.234] [Thread- 1] 🔄 Processing 500 nodes from New York...
```

### Address Accepted
```
[14:23:46.123] [Thread- 1] ✅ ACCEPTED (score: 1.0000 [1.0], total: 1/15): 123 Main St, New York...
```

### Address Rejected
```
[14:23:46.234] [Thread- 2] ❌ REJECTED (API score: 0.8500 < 0.9): 456 Invalid St...
```

### Overall Progress
```
[14:23:50.123] [MainThread] 📊 Progress: 10/200 cities processed, 5/15 addresses found
```

---

## Example: Real-Time Monitoring

### Step 1: Start the script with logging
```bash
python3 generate_address_cache.py 2>&1 | tee address_cache.log
```

### Step 2: In another terminal, monitor all threads
```bash
# Watch all threads
watch -n 1 'tail -20 address_cache.log'
```

### Step 3: Filter by thread (optional)
```bash
# Terminal 1: Thread 1
tail -f address_cache.log | grep --color=always "Thread- 1"

# Terminal 2: Thread 2
tail -f address_cache.log | grep --color=always "Thread- 2"

# Terminal 3: All accepted addresses
tail -f address_cache.log | grep --color=always "✅ ACCEPTED"
```

---

## Tips

1. **Use `tee` to save and view simultaneously**
   ```bash
   python3 generate_address_cache.py 2>&1 | tee address_cache.log
   ```

2. **Filter by message type**
   ```bash
   # Only accepted addresses
   tail -f address_cache.log | grep "✅ ACCEPTED"
   
   # Only rejected addresses
   tail -f address_cache.log | grep "❌ REJECTED"
   
   # Only progress updates
   tail -f address_cache.log | grep "📊 Progress"
   ```

3. **Count addresses found per thread**
   ```bash
   grep "✅ ACCEPTED" address_cache.log | grep -o "Thread-[0-9]*" | sort | uniq -c
   ```

4. **View timestamps to see processing speed**
   ```bash
   tail -f address_cache.log | grep -E "Thread- [0-9]" | awk '{print $1, $2, $NF}'
   ```

5. **Monitor specific city**
   ```bash
   tail -f address_cache.log | grep "New York"
   ```

---

## Troubleshooting

### Colors not showing in `tail -f`

**Solution**: Use `less -R`:
```bash
tail -f address_cache.log | less -R
```

### Too much output

**Solution**: Filter by thread or message type:
```bash
tail -f address_cache.log | grep "✅ ACCEPTED"
```

### Want to see all threads but less verbose

**Solution**: The script already filters verbose output. If you want even less, you can modify the `verbose` parameter or filter:
```bash
tail -f address_cache.log | grep -E "(Thread-|MainThread)" | grep -E "(📍|✅|📊)"
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 generate_address_cache.py` | Run with colored output |
| `python3 generate_address_cache.py 2>&1 \| tee log.txt` | Save and view simultaneously |
| `tail -f log.txt` | View in real-time |
| `tail -f log.txt \| grep "Thread- 1"` | Filter by thread |
| `tail -f log.txt \| grep "✅ ACCEPTED"` | Filter accepted addresses |
| `tail -f log.txt \| less -R` | View with colors |
| `multitail log.txt` | Multi-pane view (if installed) |

---

## Example Output

```
[14:23:45.123] [Thread- 1] 📍 City 1/200: New York (40.7128, -74.0060)
[14:23:45.234] [Thread- 2] 📍 City 2/200: Los Angeles (34.0522, -118.2437)
[14:23:45.345] [Thread- 3] 📍 City 3/200: Chicago (41.8781, -87.6298)
[14:23:45.456] [Thread- 1] 🔄 Processing 500 nodes from New York...
[14:23:46.123] [Thread- 1] ✅ ACCEPTED (score: 1.0000 [1.0], total: 1/15): 123 Main St, New York...
[14:23:46.234] [Thread- 2] 🔄 Processing 300 nodes from Los Angeles...
[14:23:46.345] [Thread- 2] ✅ ACCEPTED (score: 0.9500 [0.9], total: 2/15): 456 Sunset Blvd, Los Angeles...
[14:23:50.123] [MainThread] 📊 Progress: 10/200 cities processed, 5/15 addresses found
```

Each thread is color-coded, making it easy to track what each thread is doing!





