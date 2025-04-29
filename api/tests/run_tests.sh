#!/bin/bash
# Purpose and Objective: 
# This script runs all API test scripts in sequence and reports their status.

# Source common utilities
source "$(dirname "$0")/common.sh"

# Function to run a test and report its status
run_test() {
  local test_script=$1
  local test_name=$2
  
  print_header "RUNNING $test_name"
  
  if [ -x "$test_script" ]; then
    "$test_script"
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
      echo -e "\n${GREEN}✓ $test_name PASSED!${NC}"
      return 0
    else
      echo -e "\n${RED}✗ $test_name FAILED!${NC}"
      return 1
    fi
  else
    echo -e "${RED}Error: $test_script is not executable or does not exist.${NC}"
    return 1
  fi
}

# Array of tests to run
declare -a tests=(
  "test_user_auth.sh:User Authentication Tests"
  "test_user_complete.sh:Complete User Flow Tests"
  "test_master_data.sh:Master Data API Tests"
  "test_podcast.sh:Podcast API Tests"
  "test_episode.sh:Episode API Tests"
)

# Track overall success
overall_success=true

# Run each test
for test_info in "${tests[@]}"; do
  IFS=':' read -r test_script test_name <<< "$test_info"
  test_path="$(dirname "$0")/$test_script"
  
  run_test "$test_path" "$test_name"
  
  if [ $? -ne 0 ]; then
    overall_success=false
    echo -e "\n${RED}Test failed. Continuing with next test...${NC}"
  fi
done

# Report overall status
if [ "$overall_success" = true ]; then
  echo -e "\n${GREEN}=== ALL TESTS PASSED! ====${NC}"
  exit 0
else
  echo -e "\n${RED}=== SOME TESTS FAILED! ====${NC}"
  exit 1
fi
