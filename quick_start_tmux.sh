#!/bin/bash

echo "=========================================="
echo "🚀 Quick Start: TMUX Split Terminal"
echo "=========================================="
echo ""
echo "tmux is installed! Starting tmux session..."
echo ""
echo "📋 QUICK COMMANDS (once inside tmux):"
echo ""
echo "  Split Terminal:"
echo "    Ctrl+B, then %   → Split vertically (left/right)"
echo "    Ctrl+B, then \"   → Split horizontally (top/bottom)"
echo ""
echo "  Navigate:"
echo "    Ctrl+B, then ←   → Move to left pane"
echo "    Ctrl+B, then →   → Move to right pane"
echo "    Ctrl+B, then ↑   → Move to top pane"
echo "    Ctrl+B, then ↓   → Move to bottom pane"
echo ""
echo "  Other:"
echo "    Ctrl+B, then x   → Close current pane"
echo "    Ctrl+B, then z   → Zoom/unzoom pane"
echo "    Ctrl+B, then d   → Detach (keeps running)"
echo ""
echo "  To exit tmux:"
echo "    Type 'exit' in each pane, or"
echo "    Ctrl+B, then type :kill-session"
echo ""
echo "=========================================="
echo "Starting tmux in 3 seconds..."
echo "=========================================="
sleep 3

# Start tmux with a named session
tmux new-session -d -s split_terminal

# Split into 2 panes (vertical)
tmux split-window -h

# Split each pane horizontally (now 4 panes)
tmux select-pane -t 0
tmux split-window -v
tmux select-pane -t 2
tmux split-window -v

# Set up each pane with a helpful message
tmux select-pane -t 0
tmux send-keys "echo 'Pane 1 (Top Left) - You can run commands here'" C-m
tmux send-keys "echo 'Try: ls -la'" C-m

tmux select-pane -t 1
tmux send-keys "echo 'Pane 2 (Top Right) - Another terminal'" C-m
tmux send-keys "echo 'Try: pwd'" C-m

tmux select-pane -t 2
tmux send-keys "echo 'Pane 3 (Bottom Left) - More terminals!'" C-m
tmux send-keys "echo 'Try: date'" C-m

tmux select-pane -t 3
tmux send-keys "echo 'Pane 4 (Bottom Right) - Last pane'" C-m
tmux send-keys "echo 'Try: whoami'" C-m

# Select first pane
tmux select-pane -t 0

# Attach to session
tmux attach-session -t split_terminal





