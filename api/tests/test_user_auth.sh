#!/bin/bash
# Purpose and Objective: 
# This script tests the user authentication and profile management endpoints.

# Source common utilities
source "$(dirname "$0")/common.sh"

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
token=$(extract_json_value "$login_response" "access_token")

if [ -z "$token" ]; then
  echo -e "${RED}Failed to get access token. Login may have failed.${NC}"
  exit 1
fi

# Save token for future use
save_token "$token"

# 3. Get user profile
print_header "GET USER PROFILE"
call_api "GET" "/users/me" "" "$token"

# 4. Update user profile
print_header "UPDATE USER PROFILE"
call_api "PUT" "/users/me" '{
  "name": "Updated Test User",
  "profile_picture": "https://example.com/profile.jpg"
}' "$token"

# 5. Change password
print_header "CHANGE PASSWORD"
call_api "POST" "/users/change-password" '{
  "current_password": "password123",
  "new_password": "newpassword456"
}' "$token"

# 6. Login with new password
print_header "LOGIN WITH NEW PASSWORD"
login_response=$(call_api "POST" "/users/login" '{
  "email": "test@example.com",
  "password": "newpassword456"
}')

# Extract the new token
token=$(extract_json_value "$login_response" "access_token")

if [ ! -z "$token" ]; then
  save_token "$token"
  echo -e "${GREEN}Successfully logged in with new password!${NC}"
else
  echo -e "${RED}Failed to login with new password.${NC}"
fi

echo -e "\n${GREEN}User authentication tests completed!${NC}"
