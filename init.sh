#!/usr/bin/env bash

set -euo pipefail

echo "🔨  Updating and upgrading system packages..."
sudo apt update -yqq
sudo apt upgrade -yqq

echo
echo "🔨  Installing GitHub CLI..."
if ! command -v gh &> /dev/null; then
    sudo apt install -qq gh
else
    echo "✅  GitHub CLI is already installed."
fi

echo
echo "🔨  Authenticating GitHub CLI..."
if ! gh auth token &> /dev/null; then
    gh auth login --web -s admin:org,delete:packages,gist,repo,workflow,write:packages
fi

gh auth status

echo
echo "🔨  Setting up Git credentials..."

if ! git config --get user.name &> /dev/null; then
    read -rp "Enter your GitHub username: " git_username
    git config --global user.name "$git_username"
else
    echo "❕  Git username is already set to: $(git config --get user.name)"
fi

if ! git config --get user.email &> /dev/null; then
    read -rp "Enter your GitHub email: " git_email
    git config --global user.email "$git_email"
else
    echo "❕  Git email is already set to: $(git config --get user.email)"
fi

echo "✅  Git credentials have been set."
