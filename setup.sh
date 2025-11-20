#!/usr/bin/env bash

# Create .ssh/id_ed25519 if it doesn't exist
if [ ! -f "$HOME/.ssh/id_ed25519" ]; then
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -f "$HOME/.ssh/id_ed25519" -N ""
    echo "🔐  SSH key generated at $HOME/.ssh/id_ed25519"
else
    echo "🔐  Using existing SSH key: $HOME/.ssh/id_ed25519"
fi

# Install python3-click if not already installed
if ! python3 -c "import click" &> /dev/null; then
    echo "🔨  Installing python3-click..."
    sudo apt-get update
    sudo apt-get install -y python3-click
    echo "🐍  python3-click installed."
else
    echo "🐍  python3-click already installed."
fi

# Install multipass if not already installed
if ! command -v multipass &> /dev/null; then
    echo "🔨  Installing Multipass..."
    sudo snap install multipass --classic
    echo "🚀  Multipass installed."
else
    echo "🚀  Multipass already installed."
fi

chmod +x ./new_instance.py
chmod +x ./init.sh

echo "✅  Setup complete. You can now run ./new_instance.py to create a new Multipass instance."
