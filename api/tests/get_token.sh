#!/bin/bash
# Purpose and Objective: 
# This script logs in with a test user and saves the token for use in other test scripts.
# It can be used to quickly get a valid token without running the full user registration flow.

# Source common utilities
source "$(dirname "$0")/common.sh"

# Default credentials
EMAIL="test@example.com"
PASSWORD="newpassword456"

# Allow overriding credentials via command line arguments
if [ ! -z "$1" ]; then
  EMAIL="$1"
fi

if [ ! -z "$2" ]; then
  PASSWORD="$2"
fi

# Try to login with existing credentials
print_header "LOGIN TO GET TOKEN"
echo -e "Using credentials: $EMAIL / $PASSWORD"

login_response=$(call_api "POST" "/users/login" "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

# Extract the token
token=$(extract_json_value "$login_response" "access_token")

if [ -z "$token" ]; then
  echo -e "${RED}Failed to get access token. Login failed.${NC}" >&2
  
  # If login failed, try registering a new user
  print_header "ATTEMPTING TO REGISTER NEW USER" >&2
  register_response=$(call_api "POST" "/users/register" "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"name\":\"Test User\"}")
  
  # Try logging in again
  print_header "TRYING LOGIN AGAIN" >&2
  login_response=$(call_api "POST" "/users/login" "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
  
  # Extract token again
  token=$(extract_json_value "$login_response" "access_token")
  
  if [ -z "$token" ]; then
    echo -e "${RED}Failed to get token after registration attempt. Exiting.${NC}" >&2
    exit 1
  fi
fi

# Save token to file
save_token "$token"
echo -e "${GREEN}✓ Successfully obtained and saved token!${NC}" >&2
echo -e "${GREEN}✓ Token is saved to /tmp/podcastai_token.txt${NC}" >&2
echo -e "${GREEN}✓ You can now use this token in other test scripts.${NC}" >&2

# Output the token for use in other scripts
echo "$token"
