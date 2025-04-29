#!/bin/bash
# Purpose and Objective: 
# This script tests the complete user journey including registration, authentication,
# profile management, settings, business information, and password operations.

# Source common utilities
source "$(dirname "$0")/common.sh"

# Generate a unique timestamp for this test run
TIMESTAMP=$(date +%s)

# Set test user details with unique email
TEST_EMAIL="complete_test_${TIMESTAMP}@example.com"
TEST_PASSWORD="password123"
TEST_NAME="Complete Test User"

# Function to check if a test passed
check_success() {
  local response=$1
  local expected_key=$2
  
  if echo "$response" | grep -q "\"$expected_key\""; then
    echo -e "${GREEN}✓ Test passed!${NC}"
    return 0
  else
    echo -e "${RED}✗ Test failed!${NC}"
    echo -e "${RED}Response: $response${NC}"
    return 1
  fi
}

echo -e "${BLUE}=== STARTING COMPLETE USER JOURNEY TEST ===${NC}"
echo -e "${BLUE}This test will simulate a complete user journey from registration to password reset.${NC}"
echo -e "${BLUE}Using test email: $TEST_EMAIL${NC}"

# 1. Register a new user
print_header "1. REGISTER NEW USER"
register_response=$(call_api "POST" "/users/register" "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"name\":\"$TEST_NAME\"}")

check_success "$register_response" "id" || exit 1

# 2. Login with the new user
print_header "2. LOGIN"
login_response=$(call_api "POST" "/users/login" "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

token=$(extract_json_value "$login_response" "access_token")
if [ -z "$token" ]; then
  echo -e "${RED}Failed to get access token. Login failed.${NC}"
  exit 1
fi

save_token "$token"
echo -e "${GREEN}✓ Login successful!${NC}"

# 3. Get user profile
print_header "3. GET USER PROFILE"
profile_response=$(call_api "GET" "/users/me" "" "$token")
check_success "$profile_response" "email" || exit 1

# 4. Update user profile
print_header "4. UPDATE USER PROFILE"
update_profile_response=$(call_api "PUT" "/users/me" "{\"name\":\"Updated $TEST_NAME\",\"profile_picture\":\"https://example.com/profile.jpg\"}" "$token")

check_success "$update_profile_response" "profile_picture" || exit 1

# 5. Get user settings
print_header "5. GET USER SETTINGS"
settings_response=$(call_api "GET" "/users/settings" "" "$token")
check_success "$settings_response" "autopilot_mode" || exit 1

# 6. Update user settings
print_header "6. UPDATE USER SETTINGS"
update_settings_response=$(call_api "PUT" "/users/settings" "{\"autopilot_mode\":true,\"default_language\":\"en\",\"default_duration\":\"30:00\"}" "$token")

check_success "$update_settings_response" "default_duration" || exit 1

# 7. Create business information
print_header "7. CREATE BUSINESS INFORMATION"
business_response=$(call_api "POST" "/users/business" "{\"business_name\":\"$TEST_NAME Business\",\"business_email\":\"business@example.com\",\"business_type\":\"Technology\",\"business_website\":\"https://example.com\",\"business_description\":\"A test business for API testing\"}" "$token")

check_success "$business_response" "business_name" || exit 1

# 8. Get business information
print_header "8. GET BUSINESS INFORMATION"
get_business_response=$(call_api "GET" "/users/business" "" "$token")
check_success "$get_business_response" "business_name" || exit 1

# 9. Change password
print_header "9. CHANGE PASSWORD"
change_password_response=$(call_api "POST" "/users/change-password" "{\"current_password\":\"$TEST_PASSWORD\",\"new_password\":\"newpassword456\"}" "$token")

check_success "$change_password_response" "message" || exit 1

# 10. Login with new password
print_header "10. LOGIN WITH NEW PASSWORD"
login_new_response=$(call_api "POST" "/users/login" "{\"email\":\"$TEST_EMAIL\",\"password\":\"newpassword456\"}")

new_token=$(extract_json_value "$login_new_response" "access_token")
if [ -z "$new_token" ]; then
  echo -e "${RED}Failed to login with new password.${NC}"
  exit 1
fi

save_token "$new_token"
echo -e "${GREEN}✓ Login with new password successful!${NC}"

# 11. Request password reset
print_header "11. REQUEST PASSWORD RESET"
reset_response=$(call_api "POST" "/users/reset-password/request" "{\"email\":\"$TEST_EMAIL\"}")

# Extract the debug token (only for testing)
if echo "$reset_response" | grep -q "debug_token"; then
  reset_token=$(echo "$reset_response" | grep -o '"debug_token":"[^"]*"' | sed 's/"debug_token":"//g' | sed 's/"//g')
  
  if [ -z "$reset_token" ]; then
    reset_token=$(extract_json_value "$reset_response" "debug_token")
  fi
else
  reset_token=""
fi

if [ -z "$reset_token" ]; then
  echo -e "${RED}No reset token found in response.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Got reset token: $reset_token${NC}"

# 12. Confirm password reset
print_header "12. CONFIRM PASSWORD RESET"
confirm_reset_response=$(call_api "POST" "/users/reset-password/confirm" "{\"token\":\"$reset_token\",\"new_password\":\"resetpassword789\"}")

check_success "$confirm_reset_response" "message" || exit 1

# 13. Login with reset password
print_header "13. LOGIN WITH RESET PASSWORD"
login_reset_response=$(call_api "POST" "/users/login" "{\"email\":\"$TEST_EMAIL\",\"password\":\"resetpassword789\"}")

final_token=$(extract_json_value "$login_reset_response" "access_token")
if [ -z "$final_token" ]; then
  echo -e "${RED}Failed to login with reset password.${NC}"
  exit 1
fi

save_token "$final_token"
echo -e "${GREEN}✓ Login with reset password successful!${NC}"

# 14. Final profile check to verify authentication still works
print_header "14. FINAL PROFILE CHECK"
final_profile_response=$(call_api "GET" "/users/me" "" "$final_token")
check_success "$final_profile_response" "email" || exit 1

echo -e "\n${GREEN}=== ALL TESTS PASSED! ====${NC}"
echo -e "${GREEN}The complete user journey test was successful.${NC}"
