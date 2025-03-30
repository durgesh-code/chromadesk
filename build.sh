#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== ChromaDesk AppImage Builder ===${NC}"

# Check if the script is run from the project root
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: This script must be run from the project root directory!${NC}"
    exit 1
fi

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source .venv/bin/activate

# Verify python is working correctly
echo -e "${GREEN}Checking Python...${NC}"
if ! python --version; then
    echo -e "${RED}Error: Python not functioning correctly in the virtual environment.${NC}"
    exit 1
fi

# Install/upgrade required packages
echo -e "${GREEN}Installing required packages...${NC}"
pip install --upgrade pip
pip install --upgrade build wheel
pip install --upgrade pyinstaller
pip install -e .

# Build using PyInstaller
echo -e "${GREEN}Building with PyInstaller...${NC}"
pyinstaller --name="chromadesk" \
            --windowed \
            --onefile \
            --add-data="data:data" \
            --icon="data/icons/io.github.anantdark.chromadesk.png" \
            chromadesk/main.py

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Build successful!${NC}"
    
    # Find the executable file that was created
    if [ -f "dist/chromadesk" ]; then
        echo -e "${GREEN}Executable created: ${YELLOW}dist/chromadesk${NC}"
        echo -e "${GREEN}Making executable...${NC}"
        chmod +x "dist/chromadesk"
        
        # Create a simple wrapper script for Linux desktop integration
        echo -e "${YELLOW}Creating desktop file...${NC}"
        cp data/io.github.anantdark.chromadesk.desktop dist/
        
        echo -e "${GREEN}Build artifacts in 'dist/' directory${NC}"
        ls -la dist/
    else
        echo -e "${YELLOW}Warning: Executable file not found. Check the build output.${NC}"
    fi
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi

# Deactivate virtual environment
deactivate

echo -e "${GREEN}=== Build process completed ===${NC}" 