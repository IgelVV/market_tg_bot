#!/bin/bash

# Colors
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Disable signals
echo -e "${PURPLE}Preparations start...${NC}\n"
echo -e "${GREEN}ENABLE_SIGNALS_TO_SYNCHRONISE_DB is set to 0${NC}\n"
export ENABLE_SIGNALS_TO_SYNCHRONISE_DB=0

# Migration
echo -e "${PURPLE}Running migration...${NC}\n"
python manage.py migrate

# Fixtures
mkdir -p shop/fixtures/
cp ozon_database/shop_dump.json shop/fixtures/

echo -e "${PURPLE}Loading fixtures...${NC}\n"
python manage.py loaddata shop_dump.json

# Enable signals back
echo -e "${GREEN}ENABLE_SIGNALS_TO_SYNCHRONISE_DB is set to 1${NC}\n"
export ENABLE_SIGNALS_TO_SYNCHRONISE_DB=1
python market/settings.py