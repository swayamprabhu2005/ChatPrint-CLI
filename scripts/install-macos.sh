#!/usr/bin/env bash
# AI Conversation CLI - macOS Setup & Installer
set -e

echo -e "\033[1;36m==================================================\033[0m"
echo -e "\033[1;36m          AI Conversation CLI Setup (macOS)       \033[0m"
echo -e "\033[1;36m==================================================\033[0m"
echo ""

ARCH=$(uname -m)
echo "Checking architecture... Detected: macOS $ARCH"

TARGET_VERSION="3.10.8"
PYTHON_CMD=""

for cmd in python3.10 python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null || true)
        if [ "$VER" = "$TARGET_VERSION" ]; then
            PYTHON_CMD="$cmd"
            echo -e "\033[0;32m✓ Python $TARGET_VERSION detected ($cmd)\033[0m"
            break
        elif [ "$(echo "$VER" | cut -d'.' -f1,2)" = "3.10" ]; then
            PYTHON_CMD="$cmd"
            echo -e "\033[0;32m✓ Python $VER detected (compatible 3.10 series)\033[0m"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "\033[1;33mPython $TARGET_VERSION is recommended for macOS.\033[0m"
    echo "Official installer: https://www.python.org/ftp/python/3.10.8/python-3.10.8-macos11.pkg"
    echo "Or install via Homebrew / pyenv:"
    echo "  brew install python@3.10"
    echo ""
    read -p "Continue with default python3? [Y/n] " choice
    if [[ "$choice" =~ ^[nN] ]]; then
        echo "Setup aborted."
        exit 1
    fi
    PYTHON_CMD="python3"
fi

DEFAULT_INSTALL_DIR="$HOME/Library/Application Support/AIConversationCLI"
echo ""
read -p "Install directory [$DEFAULT_INSTALL_DIR]: " USER_DIR
INSTALL_DIR="${USER_DIR:-$DEFAULT_INSTALL_DIR}"

mkdir -p "$INSTALL_DIR"
VENV_DIR="$INSTALL_DIR/venv"

echo "Creating virtual environment at $VENV_DIR..."
"$PYTHON_CMD" -m venv "$VENV_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Installing AI Conversation CLI..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install "$REPO_ROOT"

# PATH configuration
BIN_DIR="$VENV_DIR/bin"
ZSHRC="$HOME/.zshrc"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$ZSHRC"
    echo -e "\033[0;32m✓ Added $BIN_DIR to $ZSHRC\033[0m"
fi

echo ""
echo "Running smoke test..."
"$BIN_DIR/ai-conversation" --version
"$BIN_DIR/ai-conversation" doctor

echo ""
echo -e "\033[1;32mAI Conversation CLI installed successfully!\033[0m"
echo "Restart your terminal or run: source $ZSHRC"
