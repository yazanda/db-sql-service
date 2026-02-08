# #!/bin/bash

# output_grade() {
#   local grade="$1"
#   local message="$2"
#   echo "#!/bin/bash" > vpl_execution
  
#   # Write message line by line with proper prefix
#   echo "$message" | while IFS= read -r line || [[ -n "$line" ]]; do
#     echo "echo 'Comment :=>> $line'" >> vpl_execution
#   done
  
#   echo "echo 'Grade :=>> $grade'" >> vpl_execution
#   chmod +x vpl_execution
# }

# gcc -shared -fPIC -Wall -Wextra -O2 hook_free.c -o hooks.so -ldl
# pip install prettytable
# python3 tester.py

# --- Set default values for testing (VPL will override these) ---
: "${MOODLE_USER_ID:=test_user_123}"
: "${EX_ID:=EX_TEST_001}"
: "${MOODLE_USER_NAME:=Test User}"
: "${VPL_SUBMISSION_ID:=12345}"

# --- Debug / submission metadata ---
echo "MOODLE_USER_NAME=$MOODLE_USER_NAME"
echo "MOODLE_USER_ID=$MOODLE_USER_ID"
echo "VPL_SUBMISSION_ID=$VPL_SUBMISSION_ID"
echo "EX_ID=$EX_ID"

# --- Run tester once and capture output ---
TABLE_OUTPUT=""
TEST_EXIT=0

if [[ -f tester.py ]]; then
  set +e
  TABLE_OUTPUT="$(python3 tester.py 2>&1)"
  TEST_EXIT=$?
  set -e
else
  TABLE_OUTPUT='{"error": "tester.py not found"}'
  TEST_EXIT=2
fi

echo "--- Captured test output ---"
echo "$TABLE_OUTPUT"
echo "--- Exit code: $TEST_EXIT ---"

# send output to the app via curl 
# Use localhost or set API_URL environment variable for production
# VPL_API_KEY should match the value configured in your deployment
API_URL="${API_URL:-http://localhost}"
VPL_API_KEY="${VPL_API_KEY:-CHANGE_ME_TO_A_LONG_RANDOM_SECRET}"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/v1/events" \
  -H "X-API-Key: ${VPL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "source": "vpl-submission",
  "payload": {
    "stid": "${MOODLE_USER_ID}",
    "exnum": "${EX_ID}",
    "table": ${TABLE_OUTPUT}
  }
}
EOF
)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | head -n-1)

echo "--- API Response (HTTP $HTTP_CODE) ---"
echo "$RESPONSE_BODY"

# Verify the submission by fetching it back using stid and exnum
if [[ "$HTTP_CODE" == "200" ]]; then
  echo ""
  echo "--- Verification: Fetching event with stid=$MOODLE_USER_ID and exnum=$EX_ID ---"
  curl -s -H "X-API-Key: ${VPL_API_KEY}" "${API_URL}/v1/events/${MOODLE_USER_ID}?exnum=${EX_ID}" | jq .
fi