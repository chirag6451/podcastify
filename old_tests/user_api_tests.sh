#!/bin/bash
# Purpose and Objective: 
# This script tests the user API endpoints including registration, login, 
# profile management, and user settings using CURL commands.

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

# 1. Register a new user
print_header "REGISTER NEW USER"
register_response=$(call_api "POST" "/users/register" '{
  "email": "test@example.com",
  "password": "password123",
  "name": "Test User"
}')

# 2. Login with the new user
print_header "LOGIN"
login_response=$(call_api "POST" "/users/login" '{
  "email": "test@example.com",
  "password": "password123"
}')

# Extract the token from the login response
token=$(echo $login_response | jq -r '.access_token')

# 3. Get user profile
print_header "GET USER PROFILE"
call_api "GET" "/users/me" "" "$token"

# 4. Update user profile
print_header "UPDATE USER PROFILE"
call_api "PUT" "/users/me" '{
  "name": "Updated Test User",
  "profile_picture": "https://example.com/profile.jpg"
}' "$token"

# 5. Get user settings
print_header "GET USER SETTINGS"
call_api "GET" "/users/settings" "" "$token"

# 6. Update user settings
print_header "UPDATE USER SETTINGS"
call_api "PUT" "/users/settings" '{
  "autopilot_mode": true,
  "default_language": "en",
  "default_duration": "30:00"
}' "$token"

# 7. Create business information
print_header "CREATE BUSINESS INFORMATION"
call_api "POST" "/users/business" '{
  "business_name": "Test Business",
  "business_email": "business@example.com",
  "business_type": "Technology",
  "business_website": "https://example.com",
  "business_description": "A test business for API testing"
}' "$token"

# 8. Get business information
print_header "GET BUSINESS INFORMATION"
call_api "GET" "/users/business" "" "$token"

# 9. Change password
print_header "CHANGE PASSWORD"
call_api "POST" "/users/change-password" '{
  "current_password": "password123",
  "new_password": "newpassword456"
}' "$token"

# 10. Login with new password
print_header "LOGIN WITH NEW PASSWORD"
call_api "POST" "/users/login" '{
  "email": "test@example.com",
  "password": "newpassword456"
}'

# 11. Request password reset
print_header "REQUEST PASSWORD RESET"
reset_response=$(call_api "POST" "/users/reset-password/request" '{
  "email": "test@example.com"
}')

# Extract the debug token (only for testing)
reset_token=$(echo $reset_response | jq -r '.debug_token')

# 12. Confirm password reset
print_header "CONFIRM PASSWORD RESET"
call_api "POST" "/users/reset-password/confirm" '{
  "token": "'$reset_token'",
  "new_password": "resetpassword789"
}'

# 13. Login with reset password
print_header "LOGIN WITH RESET PASSWORD"
call_api "POST" "/users/login" '{
  "email": "test@example.com",
  "password": "resetpassword789"
}'

echo -e "\n${GREEN}All tests completed!${NC}"
