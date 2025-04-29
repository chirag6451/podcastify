#!/bin/bash
# Purpose and Objective: 
# This script tests the user settings and business information endpoints.

# Source common utilities
source "$(dirname "$0")/common.sh"

# Load token from file
token=$(load_token)
if [ -z "$token" ]; then
  echo -e "${RED}No token found. Please run test_user_auth.sh first to authenticate.${NC}"
  exit 1
fi

# 1. Get user settings
print_header "GET USER SETTINGS"
call_api "GET" "/users/settings" "" "$token"

# 2. Update user settings
print_header "UPDATE USER SETTINGS"
call_api "PUT" "/users/settings" '{
  "autopilot_mode": true,
  "default_language": "en",
  "default_duration": "30:00"
}' "$token"

# 3. Create business information
print_header "CREATE BUSINESS INFORMATION"
call_api "POST" "/users/business" '{
  "business_name": "Test Business",
  "business_email": "business@example.com",
  "business_type": "Technology",
  "business_website": "https://example.com",
  "business_description": "A test business for API testing"
}' "$token"

# 4. Get business information
print_header "GET BUSINESS INFORMATION"
call_api "GET" "/users/business" "" "$token"

echo -e "\n${GREEN}User settings tests completed!${NC}"
