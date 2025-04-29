#!/bin/bash
# Purpose and Objective: 
# This script tests the episode-related API endpoints for the PodcastAI platform.
# It covers all CRUD operations and specialized endpoints for episode management.

# Source common utilities
source "$(dirname "$0")/common.sh"

# Generate a unique timestamp for this test run
timestamp=$(date +%s)

# Register a test user
print_header "REGISTER TEST USER"
register_response=$(curl -s -X POST "$BASE_URL/users/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"episode_test_${timestamp}@example.com\",\"password\":\"password123\",\"name\":\"Episode Test User ${timestamp}\"}")

echo "Register response: $register_response"
user_id=$(extract_json_value "$register_response" "id")

if [ -z "$user_id" ]; then
  echo -e "${RED}Failed to extract user ID from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully registered user with ID: $user_id${NC}"

# Login to get token
print_header "LOGIN"
login_response=$(curl -s -X POST "$BASE_URL/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"episode_test_${timestamp}@example.com\",\"password\":\"password123\"}")

echo "Login response: $login_response"
token=$(extract_json_value "$login_response" "access_token")

if [ -z "$token" ]; then
  echo -e "${RED}Failed to extract token from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully logged in and got token${NC}"

# Create a podcast group
print_header "CREATE PODCAST GROUP"
group_payload="{\"name\":\"Test Group ${timestamp}\",\"description\":\"Test group for episode testing\"}"
create_group_response=$(curl -s -X POST "$BASE_URL/podcasts/groups" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$group_payload")

echo "Create group response: $create_group_response"
group_id=$(extract_json_value "$create_group_response" "id")
if [ -z "$group_id" ]; then
  echo -e "${RED}Failed to extract group ID from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully created podcast group with ID: $group_id${NC}"

# Create a podcast
print_header "CREATE PODCAST"
podcast_payload="{\"title\":\"Test Podcast ${timestamp}\",\"description\":\"Test podcast for episode API testing\",\"language\":\"en\",\"group_id\":$group_id}"
create_podcast_response=$(curl -s -X POST "$BASE_URL/podcasts/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$podcast_payload")

echo "Create podcast response: $create_podcast_response"
podcast_id=$(extract_json_value "$create_podcast_response" "id")
if [ -z "$podcast_id" ]; then
  echo -e "${RED}Failed to extract podcast ID from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully created podcast with ID: $podcast_id${NC}"

# ===== EPISODE TESTING =====

print_header "TESTING EPISODE ENDPOINTS"

# Create an episode
print_header "CREATE EPISODE"
episode_payload="{\"podcast_id\":$podcast_id,\"title\":\"Test Episode ${timestamp}\",\"description\":\"Test episode for API testing\",\"language\":\"en\"}"
create_episode_response=$(curl -s -X POST "$BASE_URL/podcasts/episodes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$episode_payload")

echo "Create episode response: $create_episode_response"
episode_id=$(extract_json_value "$create_episode_response" "id")
if [ -z "$episode_id" ]; then
  echo -e "${RED}Failed to extract episode ID from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully created episode with ID: $episode_id${NC}"

# Get all episodes for the podcast
print_header "GET ALL EPISODES"
get_episodes_response=$(curl -s -X GET "$BASE_URL/podcasts/episodes?podcast_id=$podcast_id" \
  -H "Authorization: Bearer $token")

echo "Get episodes response: $get_episodes_response"
# Check if response contains array with at least one item
if ! echo "$get_episodes_response" | jq -e '. | length > 0' >/dev/null 2>&1; then
  echo -e "${RED}Failed to get episodes or empty response${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully retrieved episodes${NC}"

# Get specific episode
print_header "GET SPECIFIC EPISODE"
get_episode_response=$(curl -s -X GET "$BASE_URL/podcasts/episodes/$episode_id" \
  -H "Authorization: Bearer $token")

echo "Get episode response: $get_episode_response"
retrieved_id=$(extract_json_value "$get_episode_response" "id")
if [ -z "$retrieved_id" ]; then
  echo -e "${RED}Failed to get specific episode${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully retrieved episode with ID: $retrieved_id${NC}"

# Update episode
print_header "UPDATE EPISODE"
update_episode_payload="{\"title\":\"Updated Episode ${timestamp}\",\"description\":\"Updated description for testing\"}"
update_episode_response=$(curl -s -X PUT "$BASE_URL/podcasts/episodes/$episode_id" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$update_episode_payload")

echo "Update episode response: $update_episode_response"
updated_id=$(extract_json_value "$update_episode_response" "id")
if [ -z "$updated_id" ]; then
  echo -e "${RED}Failed to update episode${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully updated episode with ID: $updated_id${NC}"

# Test the status update endpoint
print_header "UPDATE EPISODE STATUS"
status_update_payload="{\"status\":\"published\"}"
status_update_response=$(curl -s -X PATCH "$BASE_URL/podcasts/episodes/$episode_id/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$status_update_payload")

echo "Status update response: $status_update_response"
updated_status=$(extract_json_value "$status_update_response" "status")
if [ "$updated_status" != "published" ]; then
  echo -e "${RED}✗ Status was not updated correctly. Expected 'published', got '$updated_status'${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully updated episode status to published${NC}"

# Create a second episode for scheduling
print_header "CREATE SECOND EPISODE FOR SCHEDULING"
episode2_payload="{\"podcast_id\":$podcast_id,\"title\":\"Scheduled Episode ${timestamp}\",\"description\":\"Test episode for scheduling\",\"language\":\"en\"}"
create_episode2_response=$(curl -s -X POST "$BASE_URL/podcasts/episodes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$episode2_payload")

echo "Create second episode response: $create_episode2_response"
episode2_id=$(extract_json_value "$create_episode2_response" "id")
if [ -z "$episode2_id" ]; then
  echo -e "${RED}Failed to extract second episode ID from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully created second episode with ID: $episode2_id${NC}"

# Schedule the second episode
print_header "SCHEDULE EPISODE"
# Schedule for 7 days in the future
future_date=$(date -v+7d -u +"%Y-%m-%dT%H:%M:%SZ")
schedule_payload="{\"publish_date\":\"$future_date\"}"
echo "Schedule payload: $schedule_payload"
schedule_response=$(curl -v -X POST "$BASE_URL/podcasts/episodes/$episode2_id/schedule" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$schedule_payload" 2>&1)

echo "Schedule response (full): $schedule_response"
# Extract just the JSON part from the verbose output
json_response=$(echo "$schedule_response" | grep -v "^*" | grep -v "^>" | grep -v "^<" | grep -v "^}" | tail -n 1)
echo "JSON response: $json_response"

scheduled_status=$(echo "$json_response" | grep -o '"status":"[^"]*"' | cut -d':' -f2 | tr -d '"')
if [ "$scheduled_status" != "scheduled" ]; then
  echo -e "${RED}✗ Status was not updated correctly. Expected 'scheduled', got '$scheduled_status'${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully scheduled episode${NC}"

# Get latest episodes
print_header "GET LATEST EPISODES"
latest_episodes_response=$(curl -s -X GET "$BASE_URL/podcasts/episodes/latest?limit=5" \
  -H "Authorization: Bearer $token")

echo "Latest episodes response: $latest_episodes_response"
# Check if response contains array
if ! echo "$latest_episodes_response" | jq -e '. | type == "array"' >/dev/null 2>&1; then
  echo -e "${RED}Failed to get latest episodes or invalid response format${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully retrieved latest episodes${NC}"

# Get scheduled episodes
print_header "GET SCHEDULED EPISODES"
scheduled_episodes_response=$(curl -s -X GET "$BASE_URL/podcasts/episodes/scheduled?days_ahead=30" \
  -H "Authorization: Bearer $token")

echo "Scheduled episodes response: $scheduled_episodes_response"
# Check if response contains array
if ! echo "$scheduled_episodes_response" | jq -e '. | type == "array"' >/dev/null 2>&1; then
  echo -e "${RED}Failed to get scheduled episodes or invalid response format${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully retrieved scheduled episodes${NC}"

# Delete episodes
print_header "DELETE EPISODES"
delete_episode_response=$(curl -s -X DELETE "$BASE_URL/podcasts/episodes/$episode_id" \
  -H "Authorization: Bearer $token")

echo "Delete episode response: $delete_episode_response"
if [ -n "$delete_episode_response" ]; then
  echo -e "${RED}✗ Delete episode should return empty response${NC}"
  exit 1
fi

delete_episode2_response=$(curl -s -X DELETE "$BASE_URL/podcasts/episodes/$episode2_id" \
  -H "Authorization: Bearer $token")

echo "Delete second episode response: $delete_episode2_response"
if [ -n "$delete_episode2_response" ]; then
  echo -e "${RED}✗ Delete episode should return empty response${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Successfully deleted episodes${NC}"

# Clean up - delete podcast
print_header "CLEANUP - DELETE PODCAST"
delete_podcast_response=$(curl -s -X DELETE "$BASE_URL/podcasts/$podcast_id" \
  -H "Authorization: Bearer $token")

echo "Delete podcast response: $delete_podcast_response"
if [ -n "$delete_podcast_response" ]; then
  echo -e "${RED}✗ Delete podcast should return empty response${NC}"
  exit 1
fi

# Clean up - delete podcast group
print_header "CLEANUP - DELETE PODCAST GROUP"
delete_group_response=$(curl -s -X DELETE "$BASE_URL/podcasts/groups/$group_id" \
  -H "Authorization: Bearer $token")

echo "Delete group response: $delete_group_response"
if [ -n "$delete_group_response" ]; then
  echo -e "${RED}✗ Delete group should return empty response${NC}"
  exit 1
fi

echo -e "${GREEN}✓ All episode tests passed successfully!${NC}"
