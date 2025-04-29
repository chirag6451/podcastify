#!/bin/bash
# Purpose and Objective: 
# This script tests the password reset functionality.

# Source common utilities
source "$(dirname "$0")/common.sh"

# 1. Request password reset
print_header "REQUEST PASSWORD RESET"
reset_response=$(call_api "POST" "/users/reset-password/request" '{
  "email": "test@example.com"
}')

# Extract the debug token (only for testing)
# First try direct extraction
if echo "$reset_response" | grep -q "debug_token"; then
  reset_token=$(echo "$reset_response" | grep -o '"debug_token":"[^"]*"' | sed 's/"debug_token":"//g' | sed 's/"//g')
  
  if [ -z "$reset_token" ]; then
    # Try with jq as fallback
    reset_token=$(extract_json_value "$reset_response" "debug_token")
  fi
else
  reset_token=""
fi

if [ -z "$reset_token" ]; then
  echo -e "${RED}No reset token found in response. Check if the email exists and if debug_token is returned.${NC}"
  echo -e "${RED}Response was: ${NC}"
  echo "$reset_response"
  exit 1
fi

echo -e "${GREEN}Got reset token: $reset_token${NC}"

# 2. Confirm password reset
print_header "CONFIRM PASSWORD RESET"
call_api "POST" "/users/reset-password/confirm" '{
  "token": "'$reset_token'",
  "new_password": "resetpassword789"
}'

# 3. Login with reset password
print_header "LOGIN WITH RESET PASSWORD"
login_response=$(call_api "POST" "/users/login" '{
  "email": "test@example.com",
  "password": "resetpassword789"
}')

# Extract the token from the login response
token=$(extract_json_value "$login_response" "access_token")

# Save token for future use
if [ ! -z "$token" ]; then
  save_token "$token"
  echo -e "${GREEN}Successfully logged in with reset password!${NC}"
else
  echo -e "${RED}Failed to login with reset password.${NC}"
fi

echo -e "\n${GREEN}Password reset tests completed!${NC}"
