#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔨 Fixing import paths in podcast app...${NC}"
echo ""

# Create necessary directories
mkdir -p podcast/tools
mkdir -p podcast/src/podcast/tools

# Create __init__.py files
find podcast -type d -not -path "*/\.*" | while read dir; do
  if [ ! -f "$dir/__init__.py" ]; then
    touch "$dir/__init__.py"
    echo -e "${GREEN}Created __init__.py in $dir${NC}"
  fi
done

# Create symbolic link
if [ -d "podcast/src/podcast/tools" ]; then
  ln -sf $(pwd)/podcast/src/podcast/tools $(pwd)/podcast/tools
  echo -e "${GREEN}Created symbolic link: podcast/tools -> podcast/src/podcast/tools${NC}"
fi

# Fix imports in key files
echo -e "${BLUE}Checking imports in app.py...${NC}"
if grep -q "from podcast.tools" podcast/app.py; then
  echo -e "${YELLOW}Found direct tool imports in app.py. These should work with the symbolic link.${NC}"
else
  echo -e "${GREEN}No problematic imports found in app.py${NC}"
fi

echo -e "${BLUE}Checking imports in crew.py...${NC}"
if grep -q "from podcast.tools" podcast/src/podcast/crew.py; then
  echo -e "${YELLOW}Found direct tool imports in crew.py. These should work with the symbolic link.${NC}"
else
  echo -e "${GREEN}No problematic imports found in crew.py${NC}"
fi

echo -e "${GREEN}✅ Import path fixes complete!${NC}"
echo ""
echo -e "${BLUE}Now run ./run-local.sh to start the application${NC}"