#!/bin/bash
# Purpose and Objective: 
# This script runs all user endpoint tests in sequence.

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Make all test scripts executable
chmod +x "$(dirname "$0")/common.sh"
chmod +x "$(dirname "$0")/test_user_auth.sh"
chmod +x "$(dirname "$0")/test_user_settings.sh"
chmod +x "$(dirname "$0")/test_password_reset.sh"

echo -e "${BLUE}=== RUNNING ALL USER API TESTS ===${NC}"

# Run authentication tests
echo -e "\n${BLUE}Running user authentication tests...${NC}"
"$(dirname "$0")/test_user_auth.sh"

# Run settings tests
echo -e "\n${BLUE}Running user settings tests...${NC}"
"$(dirname "$0")/test_user_settings.sh"

# Run password reset tests
echo -e "\n${BLUE}Running password reset tests...${NC}"
"$(dirname "$0")/test_password_reset.sh"

echo -e "\n${GREEN}All user API tests completed!${NC}"
