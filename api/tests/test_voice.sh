#!/bin/bash
# Purpose and Objective: 
# This script tests the voice-related API endpoints for retrieving and filtering Elevenlabs voices.

# Source common utilities
source "$(dirname "$0")/common.sh"

# Test getting all voices
print_header "GET ALL VOICES"
# First login to get a token
login_response=$(call_api "POST" "/users/login" "{\"email\":\"test@example.com\",\"password\":\"password123\"}")
token=$(extract_json_value "$login_response" "access_token")

if [ -z "$token" ]; then
  echo -e "${RED}Failed to get access token. Login failed.${NC}"
  exit 1
fi

save_token "$token"
echo -e "${GREEN}✓ Login successful!${NC}"

# Get all voices
voices_response=$(call_api "GET" "/voices" "" "$token")
check_response "$voices_response" "voice_id" "Failed to get voices"

# Test getting a specific voice
print_header "GET SPECIFIC VOICE"
# Extract first voice ID from the list
first_voice_id=$(echo "$voices_response" | grep -o '"voice_id":"[^"]*"' | head -1 | sed 's/"voice_id":"//g' | sed 's/"//g')

if [ -z "$first_voice_id" ]; then
  echo -e "${RED}No voice ID found in response.${NC}"
  exit 1
fi

echo "Testing with voice ID: $first_voice_id"
voice_response=$(call_api "GET" "/voices/$first_voice_id" "" "$token")
check_response "$voice_response" "voice_id" "Failed to get specific voice"

# Test filtering voices
print_header "FILTER VOICES"
filter_response=$(call_api "POST" "/voices/filter" "{\"gender\":\"female\",\"language\":\"en\"}" "$token")
check_response "$filter_response" "voice_id" "Failed to filter voices"

echo -e "\n${GREEN}=== ALL VOICE TESTS PASSED! ====${NC}"
echo -e "${GREEN}The voice API endpoints are working correctly.${NC}"
