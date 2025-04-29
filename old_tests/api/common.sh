#!/bin/bash
# Purpose and Objective: 
# This script provides common utilities for API testing with CURL commands.

# Set the base URL
BASE_URL="http://0.0.0.0:8011/api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
  echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Function to make API calls and format the response
call_api() {
  local method=$1
  local endpoint=$2
  local data=$3
  local token=$4
  
  echo -e "${GREEN}Request:${NC} $method $endpoint"
  if [ ! -z "$data" ]; then
    echo -e "${GREEN}Data:${NC} $data"
  fi
  
  if [ ! -z "$token" ]; then
    echo -e "${GREEN}Using token:${NC} $token"
    response=$(curl -s -X $method "$BASE_URL$endpoint" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $token" \
      -d "$data")
  else
    response=$(curl -s -X $method "$BASE_URL$endpoint" \
      -H "Content-Type: application/json" \
      -d "$data")
  fi
  
  echo -e "${GREEN}Response:${NC}"
  echo $response | jq '.' || echo $response
  echo ""
  
  # Return the response for further processing
  echo $response
}

# Function to save token to file
save_token() {
  local token=$1
  echo $token > /tmp/podcastai_token.txt
  echo -e "${GREEN}Token saved to /tmp/podcastai_token.txt${NC}"
}

# Function to load token from file
load_token() {
  if [ -f /tmp/podcastai_token.txt ]; then
    token=$(cat /tmp/podcastai_token.txt)
    echo $token
  else
    echo ""
  fi
}
