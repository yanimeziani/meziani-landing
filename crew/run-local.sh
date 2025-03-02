#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting PodcasterZ local development environment${NC}"
echo ""

# Check for .env file
if [ ! -f .env ]; then
  echo -e "${YELLOW}⚠️  .env file not found, creating a template. Please edit it with your API keys.${NC}"
  cp .env.example .env 2>/dev/null || touch .env
  echo "# Add your API keys below (required)" >> .env
  echo "SERPER_API_KEY=your_serper_key_here" >> .env
  echo "ELEVENLABS_API_KEY=your_elevenlabs_key_here" >> .env
  echo "CURRENT_YEAR=2025" >> .env
  echo "" >> .env
  echo -e "${YELLOW}Created .env file. Please edit it and run this script again.${NC}"
  exit 1
fi

# Run structure check
echo -e "${BLUE}Checking directory structure...${NC}"
./check-structure.sh

# Create necessary directories
echo -e "${BLUE}Creating data directories...${NC}"
mkdir -p data/podcasts
mkdir -p data/research

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Check if port 5200 is already in use
if lsof -i:5200 -sTCP:LISTEN > /dev/null 2>&1; then
  echo -e "${YELLOW}⚠️  Port 5200 is already in use. The app will be available at a different port.${NC}"
fi

# Build and run the Docker container
echo -e "${GREEN}🚀 Building and starting the local CrewAI podcast app...${NC}"
echo -e "${BLUE}This may take a few minutes for the first build...${NC}"
docker-compose -f docker-compose.local.yml up --build

# This part runs after Ctrl+C
echo -e "${BLUE}Stopping containers...${NC}"
docker-compose -f docker-compose.local.yml down