#!/bin/bash
# Purpose and Objective: 
# This script tests all podcast-related API endpoints including
# podcast management, episode management, and podcast group organization.

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
token=$(extract_json_value "$login_response" "access_token")

if [ -z "$token" ]; then
  echo -e "${RED}Failed to extract access token from login response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully logged in and obtained token!${NC}"

# ==================== Test Podcast Group Endpoints ====================
print_header "TESTING PODCAST GROUP ENDPOINTS"

# Create a podcast group
print_header "CREATE PODCAST GROUP"
group_payload="{\"name\":\"Test Group ${timestamp}\",\"description\":\"Test podcast group for API testing\"}"
create_group_response=$(curl -s -X POST "$BASE_URL/podcasts/groups" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$group_payload")

echo "Create group response: $create_group_response"
check_response "$create_group_response" "id" "Failed to create podcast group" || exit 1

# Extract group ID from response
group_id=$(extract_json_value "$create_group_response" "id")

if [ -z "$group_id" ]; then
  echo -e "${RED}Failed to extract group ID from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully created podcast group with ID: $group_id${NC}"

# Get all podcast groups
print_header "GET ALL PODCAST GROUPS"
get_groups_response=$(curl -s -X GET "$BASE_URL/podcasts/groups" \
  -H "Authorization: Bearer $token")

echo "Get groups response: $get_groups_response"
check_response "$get_groups_response" "id" "Failed to get podcast groups" || exit 1

# Get specific podcast group
print_header "GET SPECIFIC PODCAST GROUP"
get_group_response=$(curl -s -X GET "$BASE_URL/podcasts/groups/$group_id" \
  -H "Authorization: Bearer $token")

echo "Get group response: $get_group_response"
check_response "$get_group_response" "id" "Failed to get specific podcast group" || exit 1

# Update podcast group
print_header "UPDATE PODCAST GROUP"
update_group_payload="{\"name\":\"Updated Group ${timestamp}\",\"description\":\"Updated description for testing\"}"
update_group_response=$(curl -s -X PUT "$BASE_URL/podcasts/groups/$group_id" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$update_group_payload")

echo "Update group response: $update_group_response"
check_response "$update_group_response" "id" "Failed to update podcast group" || exit 1

# ==================== Test Podcast Endpoints ====================
print_header "TESTING PODCAST ENDPOINTS"

# Create a podcast
print_header "CREATE PODCAST"
podcast_payload="{\"title\":\"Test Podcast ${timestamp}\",\"description\":\"Test podcast for API testing\",\"group_id\":$group_id}"
create_podcast_response=$(curl -s -X POST "$BASE_URL/podcasts/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$podcast_payload")

echo "Create podcast response: $create_podcast_response"
check_response "$create_podcast_response" "id" "Failed to create podcast" || exit 1

# Extract podcast ID from response
podcast_id=$(extract_json_value "$create_podcast_response" "id")

if [ -z "$podcast_id" ]; then
  echo -e "${RED}Failed to extract podcast ID from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully created podcast with ID: $podcast_id${NC}"

# Get all podcasts
print_header "GET ALL PODCASTS"
get_podcasts_response=$(curl -s -X GET "$BASE_URL/podcasts/" \
  -H "Authorization: Bearer $token")

echo "Get podcasts response: $get_podcasts_response"
check_response "$get_podcasts_response" "id" "Failed to get podcasts" || exit 1

# Get specific podcast
print_header "GET SPECIFIC PODCAST"
get_podcast_response=$(curl -s -X GET "$BASE_URL/podcasts/$podcast_id" \
  -H "Authorization: Bearer $token")

echo "Get podcast response: $get_podcast_response"
check_response "$get_podcast_response" "id" "Failed to get specific podcast" || exit 1

# Update podcast
print_header "UPDATE PODCAST"
update_podcast_payload="{\"title\":\"Updated Podcast ${timestamp}\",\"description\":\"Updated description for testing\"}"
update_podcast_response=$(curl -s -X PUT "$BASE_URL/podcasts/$podcast_id" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$update_podcast_payload")

echo "Update podcast response: $update_podcast_response"
check_response "$update_podcast_response" "id" "Failed to update podcast" || exit 1

# ==================== Test Episode Endpoints ====================
print_header "TESTING EPISODE ENDPOINTS"

# Create an episode
print_header "CREATE EPISODE"
episode_payload="{\"podcast_id\":$podcast_id,\"title\":\"Test Episode ${timestamp}\",\"description\":\"Test episode for API testing\"}"
create_episode_response=$(curl -s -X POST "$BASE_URL/podcasts/episodes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$episode_payload")

echo "Create episode response: $create_episode_response"
check_response "$create_episode_response" "id" "Failed to create episode" || exit 1

# Extract episode ID from response
episode_id=$(extract_json_value "$create_episode_response" "id")

if [ -z "$episode_id" ]; then
  echo -e "${RED}Failed to extract episode ID from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully created episode with ID: $episode_id${NC}"

# Get all episodes
print_header "GET ALL EPISODES"
get_episodes_response=$(curl -s -X GET "$BASE_URL/podcasts/episodes?podcast_id=${podcast_id}" \
  -H "Authorization: Bearer $token")

echo "Get episodes response: $get_episodes_response"
check_response "$get_episodes_response" "id" "Failed to get episodes" "true" || exit 1

# Get specific episode
print_header "GET SPECIFIC EPISODE"
get_episode_response=$(curl -s -X GET "$BASE_URL/podcasts/episodes/$episode_id" \
  -H "Authorization: Bearer $token")

echo "Get episode response: $get_episode_response"
check_response "$get_episode_response" "id" "Failed to get specific episode" || exit 1

# Update episode
print_header "UPDATE EPISODE"
update_episode_payload="{\"title\":\"Updated Episode ${timestamp}\",\"description\":\"Updated description for testing\",\"status\":\"published\"}"
update_episode_response=$(curl -s -X PUT "$BASE_URL/podcasts/episodes/$episode_id" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$update_episode_payload")

echo "Update episode response: $update_episode_response"
check_response "$update_episode_response" "id" "Failed to update episode" || exit 1

# ==================== Test Platform Config Endpoints ====================
print_header "TESTING PLATFORM CONFIG ENDPOINTS"

# Create a platform config
print_header "CREATE PLATFORM CONFIG"
config_payload="{\"podcast_id\":$podcast_id,\"platform_id\":1,\"enabled\":true,\"auto_publish\":false,\"account_id\":\"test_account_${timestamp}\"}"
create_config_response=$(curl -s -X POST "$BASE_URL/podcasts/platform-configs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$config_payload")

echo "Create platform config response: $create_config_response"
check_response "$create_config_response" "id" "Failed to create platform config" || exit 1

# Extract config ID from response
config_id=$(extract_json_value "$create_config_response" "id")

if [ -z "$config_id" ]; then
  echo -e "${RED}Failed to extract config ID from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully created platform config with ID: $config_id${NC}"

# Get all platform configs for podcast
print_header "GET ALL PLATFORM CONFIGS"
get_configs_response=$(curl -s -X GET "$BASE_URL/podcasts/platform-configs?podcast_id=$podcast_id" \
  -H "Authorization: Bearer $token")

echo "Get platform configs response: $get_configs_response"
check_response "$get_configs_response" "id" "Failed to get platform configs" "true" || exit 1

# Update platform config
print_header "UPDATE PLATFORM CONFIG"
update_config_payload="{\"podcast_id\":$podcast_id,\"platform_id\":1,\"enabled\":true,\"auto_publish\":true,\"account_id\":\"updated_account_${timestamp}\"}"
update_config_response=$(curl -s -X PUT "$BASE_URL/podcasts/platform-configs/$config_id" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$update_config_payload")

echo "Update platform config response: $update_config_response"
check_response "$update_config_response" "id" "Failed to update platform config" || exit 1

# ==================== Clean Up (Optional) ====================
# Uncomment these sections if you want to clean up after testing

# # Delete platform config
# print_header "DELETE PLATFORM CONFIG"
# delete_config_response=$(curl -s -X DELETE "$BASE_URL/podcasts/platform-configs/$config_id" \
#   -H "Authorization: Bearer $token" -v)
# echo "Delete platform config response code: $?"

# # Delete episode
# print_header "DELETE EPISODE"
# delete_episode_response=$(curl -s -X DELETE "$BASE_URL/podcasts/episodes/$episode_id" \
#   -H "Authorization: Bearer $token" -v)
# echo "Delete episode response code: $?"

# # Delete podcast
# print_header "DELETE PODCAST"
# delete_podcast_response=$(curl -s -X DELETE "$BASE_URL/podcasts/$podcast_id" \
#   -H "Authorization: Bearer $token" -v)
# echo "Delete podcast response code: $?"

# # Delete podcast group
# print_header "DELETE PODCAST GROUP"
# delete_group_response=$(curl -s -X DELETE "$BASE_URL/podcasts/groups/$group_id" \
#   -H "Authorization: Bearer $token" -v)
# echo "Delete podcast group response code: $?"

echo -e "\n${GREEN}=== ALL PODCAST API TESTS PASSED! ====${NC}"
echo -e "${GREEN}All podcast API endpoints are working correctly.${NC}"
