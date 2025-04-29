#!/bin/bash
# Purpose and Objective: 
# This script tests all master data API endpoints including voices, conversation styles,
# video styles, profile types, and platforms.

# Source common utilities
source "$(dirname "$0")/common.sh"

# Function to check if a test passed
check_response() {
  local response=$1
  local expected_key=$2
  local error_message=$3
  local allow_empty=${4:-false}
  
  # If we allow empty arrays and the response is an empty array, consider it a pass
  if [[ "$allow_empty" == "true" ]]; then
    # Check if response is an empty array
    if [[ "$response" == "[]" || "$response" == *"[]"* ]]; then
      echo -e "${GREEN}✓ Test passed! (Empty array response accepted)${NC}"
      return 0
    fi
  fi
  
  if echo "$response" | grep -q "\"$expected_key\""; then
    echo -e "${GREEN}✓ Test passed!${NC}"
    return 0
  else
    echo -e "${RED}✗ Test failed! $error_message${NC}"
    echo -e "${RED}Response: $response${NC}"
    return 1
  fi
}

# Create a random user with timestamp to ensure uniqueness
print_header "CREATING TEST USER"
timestamp=$(date +%s)
test_email="test_user_${timestamp}@example.com"
test_password="password123"
test_name="Test User ${timestamp}"

register_payload="{\"email\":\"$test_email\",\"password\":\"$test_password\",\"name\":\"$test_name\"}"
register_response=$(curl -s -X POST "$BASE_URL/users/register" \
  -H "Content-Type: application/json" \
  -d "$register_payload")

echo "Register response: $register_response"
check_response "$register_response" "id" "Failed to register test user" || exit 1
echo -e "${GREEN}✓ Successfully registered test user: $test_email${NC}"

# Login with the new user to get token
print_header "LOGGING IN WITH TEST USER"
login_payload="{\"email\":\"$test_email\",\"password\":\"$test_password\"}"
login_response=$(curl -s -X POST "$BASE_URL/users/login" \
  -H "Content-Type: application/json" \
  -d "$login_payload")

echo "Login response: $login_response"
check_response "$login_response" "access_token" "Failed to login with test user" || exit 1

# Extract token from login response
token=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"//g' | sed 's/"//g')

if [ -z "$token" ]; then
  echo -e "${RED}Failed to extract access token from login response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully logged in and obtained token!${NC}"

# Function to test CRUD operations for a style entity
test_style_entity() {
  local entity_type=$1
  local endpoint=$2
  local create_name=$3
  local create_desc=$4
  
  # Test GET all
  print_header "GET ALL ${entity_type^^}"
  local get_all_response=$(call_api "GET" "$endpoint" "" "$token")
  check_response "$get_all_response" "id" "Failed to get all $entity_type" "true" || return 1
  
  # Test POST (create)
  print_header "CREATE ${entity_type^^}"
  local create_payload="{\"name\":\"$create_name\",\"description\":\"$create_desc\"}"
  local create_response=$(call_api "POST" "$endpoint" "$create_payload" "$token")
  
  check_response "$create_response" "id" "Failed to create $entity_type" || return 1
  
  # Extract ID from create response
  local entity_id=$(extract_json_value "$create_response" "id")
  
  if [ -z "$entity_id" ]; then
    echo -e "${RED}Failed to extract entity ID from response.${NC}"
    return 1
  fi
  
  # Test GET by ID
  print_header "GET ${entity_type^^} BY ID"
  local get_by_id_response=$(call_api "GET" "$endpoint/$entity_id" "" "$token")
  check_response "$get_by_id_response" "id" "Failed to get $entity_type by ID" || return 1
  
  echo -e "${GREEN}✓ All $entity_type tests passed!${NC}"
  return 0
}

# Test Voice Endpoints
print_header "TESTING VOICE ENDPOINTS"

# Get all voices
print_header "GET ALL VOICES"
voices_response=$(call_api "GET" "/voices/" "" "$token")
check_response "$voices_response" "voice_id" "Failed to get voices" || exit 1

# Test filtering voices
print_header "FILTER VOICES"
filter_payload="{\"gender\":\"female\",\"language\":\"en\"}"

# Use curl directly for filter endpoint to avoid issues with call_api function
filter_response=$(curl -s -X POST "$BASE_URL/voices/filter" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$filter_payload")

echo -e "${GREEN}Filter response: $filter_response${NC}"

# Check if it's a valid JSON array (empty arrays are valid)
if [[ "$filter_response" == "[]" || $(echo "$filter_response" | jq -e 'if type=="array" then true else false end' 2>/dev/null) == "true" ]]; then
  echo -e "${GREEN}✓ Test passed! Filter endpoint returned a valid JSON array.${NC}"
else
  echo -e "${RED}✗ Test failed! Filter endpoint did not return a valid JSON array.${NC}"
  echo -e "${RED}Response: $filter_response${NC}"
  exit 1
fi

# If there are voices, test getting a specific voice
if [[ "$voices_response" != "[]" && "$voices_response" != "{}" ]]; then
  print_header "GET SPECIFIC VOICE"
  # Extract first voice ID from the list
  first_voice_id=$(echo "$voices_response" | grep -o '"voice_id":"[^"]*"' | head -1 | sed 's/"voice_id":"//g' | sed 's/"//g')
  
  if [ -n "$first_voice_id" ]; then
    echo "Testing with voice ID: $first_voice_id"
    voice_response=$(call_api "GET" "/voices/$first_voice_id" "" "$token")
    check_response "$voice_response" "voice_id" "Failed to get specific voice" || exit 1
  fi
fi

echo -e "${GREEN}✓ Voice endpoint tests passed!${NC}"

# Test Conversation Style Endpoints
print_header "TESTING CONVERSATION STYLE ENDPOINTS"
test_style_entity "conversation style" "/styles/conversation" "Test Conversation Style ${timestamp}" "Test description for conversation style" || exit 1

# Test Video Style Endpoints
print_header "TESTING VIDEO STYLE ENDPOINTS"
test_style_entity "video style" "/styles/video" "Test Video Style ${timestamp}" "Test description for video style" || exit 1

# Test Profile Type Endpoints
print_header "TESTING PROFILE TYPE ENDPOINTS"
test_style_entity "profile type" "/styles/profile-types" "Test Profile Type ${timestamp}" "Test description for profile type" || exit 1

# Test Platform Endpoints
print_header "TESTING PLATFORM ENDPOINTS"
# Test GET all platforms
print_header "GET ALL PLATFORMS"
platforms_response=$(call_api "GET" "/styles/platforms" "" "$token")
check_response "$platforms_response" "id" "Failed to get all platforms" "true" || exit 1

# Test POST (create) platform
print_header "CREATE PLATFORM"
platform_payload="{\"name\":\"Test Platform ${timestamp}\",\"description\":\"Test platform for distribution\",\"icon_url\":\"https://example.com/icon.png\"}"
create_platform_response=$(call_api "POST" "/styles/platforms" "$platform_payload" "$token")

check_response "$create_platform_response" "id" "Failed to create platform" || exit 1

# Extract ID from create response
platform_id=$(extract_json_value "$create_platform_response" "id")

if [ -z "$platform_id" ]; then
  echo -e "${RED}Failed to extract platform ID from response.${NC}"
  exit 1
fi

# Test GET platform by ID
print_header "GET PLATFORM BY ID"
get_platform_response=$(call_api "GET" "/styles/platforms/$platform_id" "" "$token")
check_response "$get_platform_response" "id" "Failed to get platform by ID" || exit 1

echo -e "${GREEN}✓ Platform endpoint tests passed!${NC}"

echo -e "\n${GREEN}=== ALL MASTER DATA TESTS PASSED! ====${NC}"
echo -e "${GREEN}All master data API endpoints are working correctly.${NC}"
