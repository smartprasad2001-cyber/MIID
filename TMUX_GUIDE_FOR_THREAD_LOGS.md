# TMUX Guide: Viewing Thread Logs

## What is TMUX?

**tmux** (Terminal Multiplexer) allows you to:
- Split your terminal into multiple panes
- View multiple things simultaneously
- Keep sessions running even if you disconnect
- Switch between different terminal views easily

---

## Installation

### macOS
```bash
brew install tmux
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install tmux
```

### Linux (CentOS/RHEL)
```bash
sudo yum install tmux
```

---

## Basic TMUX Commands

### Starting TMUX

```bash
# Start a new tmux session
tmux

# Start with a custom name
tmux new -s logs

# List all sessions
tmux ls
```

### The Prefix Key

**All tmux commands start with a prefix key: `Ctrl+B`**

Press `Ctrl+B`, then release, then press the command key.

---

## Essential Commands

### Splitting Panes

| Command | Action |
|---------|--------|
| `Ctrl+B` then `%` | Split vertically (left/right) |
| `Ctrl+B` then `"` | Split horizontally (top/bottom) |
| `Ctrl+B` then `x` | Close current pane |
| `Ctrl+B` then `z` | Zoom/unzoom current pane (fullscreen toggle) |

### Navigating Between Panes

| Command | Action |
|---------|--------|
| `Ctrl+B` then `←` | Move to left pane |
| `Ctrl+B` then `→` | Move to right pane |
| `Ctrl+B` then `↑` | Move to top pane |
| `Ctrl+B` then `↓` | Move to bottom pane |
| `Ctrl+B` then `q` | Show pane numbers (then press number to jump) |

### Resizing Panes

| Command | Action |
|---------|--------|
| `Ctrl+B` then `Ctrl+←` | Resize left |
| `Ctrl+B` then `Ctrl+→` | Resize right |
| `Ctrl+B` then `Ctrl+↑` | Resize up |
| `Ctrl+B` then `Ctrl+↓` | Resize down |

### Scrolling

| Command | Action |
|---------|--------|
| `Ctrl+B` then `[` | Enter copy mode (scroll mode) |
| `↑` `↓` | Scroll up/down (in copy mode) |
| `q` | Exit copy mode |

---

## Step-by-Step: Viewing Thread Logs

### Step 1: Start the Script with Logging

**Terminal 1:**
```bash
cd /Users/prasad/cursor/MIID-subnet
python3 generate_address_cache.py 2>&1 | tee address_cache.log
```

### Step 2: Start TMUX

**Terminal 2:**
```bash
tmux new -s thread_logs
```

### Step 3: Split into Multiple Panes

You'll see a single pane. Now split it:

1. **Split vertically (left/right):**
   - Press `Ctrl+B`
   - Release
   - Press `%`
   - You now have 2 panes side-by-side

2. **Split horizontally (top/bottom) in left pane:**
   - Move to left pane: `Ctrl+B` then `←`
   - Split: `Ctrl+B` then `"`

3. **Split horizontally in right pane:**
   - Move to right pane: `Ctrl+B` then `→`
   - Split: `Ctrl+B` then `"`

**You now have 4 panes!**

### Step 4: Arrange Panes (Optional)

If you want a different layout:

**2x2 Grid:**
```
┌─────────┬─────────┐
│  Pane 1 │  Pane 2 │
├─────────┼─────────┤
│  Pane 3 │  Pane 4 │
└─────────┴─────────┘
```

**4 Panes in a Row:**
```
┌─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │
└─────┴─────┴─────┴─────┘
```

### Step 5: View Different Threads in Each Pane

In each pane, run a filtered `tail -f` command:

**Pane 1 (Top Left):**
```bash
tail -f address_cache.log | grep --color=always "Thread- 1"
```

**Pane 2 (Top Right):**
```bash
tail -f address_cache.log | grep --color=always "Thread- 2"
```

**Pane 3 (Bottom Left):**
```bash
tail -f address_cache.log | grep --color=always "Thread- 3"
```

**Pane 4 (Bottom Right):**
```bash
tail -f address_cache.log | grep --color=always "Thread- 4"
```

### Step 6: Navigate Between Panes

- `Ctrl+B` then `←` → Move left
- `Ctrl+B` then `→` → Move right
- `Ctrl+B` then `↑` → Move up
- `Ctrl+B` then `↓` → Move down

---

## Advanced: 8 Panes for All Threads

### Create 8 Panes

1. Start with 1 pane
2. Split vertically: `Ctrl+B` then `%` (2 panes)
3. Split each vertically again: `Ctrl+B` then `%` (4 panes)
4. Split each horizontally: `Ctrl+B` then `"` (8 panes)

### Assign Threads to Panes

**Pane 1:** `tail -f address_cache.log | grep --color=always "Thread- 1"`
**Pane 2:** `tail -f address_cache.log | grep --color=always "Thread- 2"`
**Pane 3:** `tail -f address_cache.log | grep --color=always "Thread- 3"`
**Pane 4:** `tail -f address_cache.log | grep --color=always "Thread- 4"`
**Pane 5:** `tail -f address_cache.log | grep --color=always "Thread- 5"`
**Pane 6:** `tail -f address_cache.log | grep --color=always "Thread- 6"`
**Pane 7:** `tail -f address_cache.log | grep --color=always "Thread- 7"`
**Pane 8:** `tail -f address_cache.log | grep --color=always "Thread- 8"`

---

## Alternative: View by Message Type

Instead of threads, view by message type:

**Pane 1:** All accepted addresses
```bash
tail -f address_cache.log | grep --color=always "✅ ACCEPTED"
```

**Pane 2:** All rejected addresses
```bash
tail -f address_cache.log | grep --color=always "❌ REJECTED"
```

**Pane 3:** Progress updates
```bash
tail -f address_cache.log | grep --color=always "📊 Progress"
```

**Pane 4:** City processing
```bash
tail -f address_cache.log | grep --color=always "📍 City"
```

---

## Useful TMUX Shortcuts

### Session Management

| Command | Action |
|---------|--------|
| `Ctrl+B` then `d` | Detach from session (keeps running) |
| `tmux attach -t logs` | Reattach to session named "logs" |
| `Ctrl+B` then `s` | List sessions and switch |
| `Ctrl+B` then `$` | Rename current session |

### Window Management

| Command | Action |
|---------|--------|
| `Ctrl+B` then `c` | Create new window |
| `Ctrl+B` then `n` | Next window |
| `Ctrl+B` then `p` | Previous window |
| `Ctrl+B` then `w` | List windows |
| `Ctrl+B` then `,` | Rename current window |

### Copy Mode (Scrolling)

| Command | Action |
|---------|--------|
| `Ctrl+B` then `[` | Enter copy mode |
| `Space` | Start selection |
| `Enter` | Copy selection |
| `Ctrl+B` then `]` | Paste |
| `q` | Exit copy mode |

---

## Quick Setup Script

Create a script to automate the setup:

**File: `setup_tmux_logs.sh`**
```bash
#!/bin/bash

# Check if log file exists
if [ ! -f "address_cache.log" ]; then
    echo "⚠️  address_cache.log not found!"
    echo "Run the script first: python3 generate_address_cache.py 2>&1 | tee address_cache.log"
    exit 1
fi

# Start tmux session
tmux new-session -d -s thread_logs

# Split into 4 panes (2x2 grid)
tmux split-window -h
tmux split-window -v
tmux select-pane -t 0
tmux split-window -v

# Set up each pane with filtered tail
tmux select-pane -t 0
tmux send-keys "tail -f address_cache.log | grep --color=always 'Thread- 1'" C-m

tmux select-pane -t 1
tmux send-keys "tail -f address_cache.log | grep --color=always 'Thread- 2'" C-m

tmux select-pane -t 2
tmux send-keys "tail -f address_cache.log | grep --color=always 'Thread- 3'" C-m

tmux select-pane -t 3
tmux send-keys "tail -f address_cache.log | grep --color=always 'Thread- 4'" C-m

# Attach to session
tmux attach-session -t thread_logs
```

**Make it executable:**
```bash
chmod +x setup_tmux_logs.sh
```

**Run it:**
```bash
./setup_tmux_logs.sh
```

---

## Example Workflow

### Complete Setup

**Terminal 1: Run the script**
```bash
cd /Users/prasad/cursor/MIID-subnet
python3 generate_address_cache.py 2>&1 | tee address_cache.log
```

**Terminal 2: Start tmux and view logs**
```bash
cd /Users/prasad/cursor/MIID-subnet
tmux new -s logs

# In tmux:
# 1. Split: Ctrl+B, then %
# 2. Split again: Ctrl+B, then "
# 3. Move to pane 1: Ctrl+B, then ←, then ↑
# 4. Run: tail -f address_cache.log | grep "Thread- 1"
# 5. Move to pane 2: Ctrl+B, then →
# 6. Run: tail -f address_cache.log | grep "Thread- 2"
# ... and so on
```

---

## Tips and Tricks

### 1. Synchronize Panes

To send the same command to all panes:
```bash
# In tmux, set synchronize-panes
Ctrl+B, then type: :setw synchronize-panes
```

### 2. Zoom a Pane

Focus on one pane:
- `Ctrl+B` then `z` - Zoom/unzoom current pane

### 3. Swap Panes

- `Ctrl+B` then `{` - Swap with previous pane
- `Ctrl+B` then `}` - Swap with next pane

### 4. Kill All Panes Except Current

- `Ctrl+B` then `:` then type `kill-pane -a`

### 5. Resize to Equal Size

- `Ctrl+B` then `:` then type `select-layout even-horizontal` (or `even-vertical`)

---

## Troubleshooting

### Can't see colors in tmux

**Solution:** Make sure your terminal supports 256 colors:
```bash
# In tmux, check:
echo $TERM
# Should be: screen-256color or tmux-256color

# If not, add to ~/.tmux.conf:
set -g default-terminal "screen-256color"
```

### Panes are too small

**Solution:** 
- Resize: `Ctrl+B` then `Ctrl+←/→/↑/↓`
- Or zoom: `Ctrl+B` then `z`

### Can't scroll in a pane

**Solution:**
- Enter copy mode: `Ctrl+B` then `[`
- Scroll with arrow keys
- Exit: Press `q`

### Lost connection, session still running?

**Solution:**
```bash
# List sessions
tmux ls

# Reattach
tmux attach -t session_name
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│         TMUX QUICK REFERENCE            │
├─────────────────────────────────────────┤
│ Prefix: Ctrl+B (then release)          │
│                                         │
│ Split:                                  │
│   %  = Vertical (left/right)           │
│   "  = Horizontal (top/bottom)        │
│                                         │
│ Navigate:                               │
│   ← → ↑ ↓ = Move between panes        │
│                                         │
│ Other:                                  │
│   x  = Close pane                      │
│   z  = Zoom/unzoom                     │
│   [  = Scroll mode                     │
│   d  = Detach                          │
│   q  = Show pane numbers               │
└─────────────────────────────────────────┘
```

---

## Summary

**For viewing thread logs:**

1. **Start script:** `python3 generate_address_cache.py 2>&1 | tee address_cache.log`
2. **Start tmux:** `tmux new -s logs`
3. **Split panes:** `Ctrl+B` then `%` (vertical), `Ctrl+B` then `"` (horizontal)
4. **In each pane:** `tail -f address_cache.log | grep "Thread- X"`
5. **Navigate:** `Ctrl+B` then arrow keys
6. **Detach:** `Ctrl+B` then `d` (keeps running)
7. **Reattach:** `tmux attach -t logs`

Now you can see all threads working simultaneously! 🎉





