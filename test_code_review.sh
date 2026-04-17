#!/bin/bash

# Code Review Feature Test Script
# Tests all three review endpoints with various code samples

echo "=================================="
echo "Code Review Feature Test Suite"
echo "=================================="
echo ""

API_URL="http://localhost:8000/api/v1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test an endpoint
test_endpoint() {
    local test_name="$1"
    local endpoint="$2"
    local payload="$3"
    
    echo "Testing: $test_name"
    echo "Endpoint: $endpoint"
    echo "---"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ HTTP 200 OK${NC}"
        
        # Check if response has issues
        issue_count=$(echo "$body" | jq -r '.issues | length' 2>/dev/null || echo "0")
        total_issues=$(echo "$body" | jq -r '.summary.total_issues' 2>/dev/null || echo "0")
        
        echo "Issues found: $total_issues"
        
        if [ "$total_issues" -gt 0 ]; then
            echo -e "${GREEN}✓ Issues detected${NC}"
            echo "$body" | jq -r '.issues[] | "  - [\(.severity)] \(.title)"' 2>/dev/null
        else
            echo -e "${YELLOW}⚠ No issues detected${NC}"
        fi
        
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ HTTP $http_code${NC}"
        echo "Response: $body"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    echo ""
}

# ============================================================================
# Test 1: Simple Python Code (should have no issues)
# ============================================================================

test_endpoint \
    "Test 1: Simple Python Function" \
    "/review" \
    '{
        "code": "def add(a, b):\n    \"\"\"Add two numbers.\"\"\"\n    return a + b",
        "language": "python"
    }'

# ============================================================================
# Test 2: SQL Injection Vulnerability (should detect security issue)
# ============================================================================

test_endpoint \
    "Test 2: SQL Injection Vulnerability" \
    "/review" \
    '{
        "code": "async function fetchUser(userId) {\n  const query = `SELECT * FROM users WHERE id = '\''${userId}'\''`;\n  return await db.execute(query);\n}",
        "language": "javascript"
    }'

# ============================================================================
# Test 3: Missing Error Handling (should detect error handling issue)
# ============================================================================

test_endpoint \
    "Test 3: Missing Error Handling" \
    "/review" \
    '{
        "code": "def divide(a, b):\n    return a / b",
        "language": "python"
    }'

# ============================================================================
# Test 4: Performance Issue (should detect inefficiency)
# ============================================================================

test_endpoint \
    "Test 4: Performance Issue" \
    "/review" \
    '{
        "code": "def find_duplicates(arr):\n    duplicates = []\n    for i in range(len(arr)):\n        for j in range(i+1, len(arr)):\n            if arr[i] == arr[j] and arr[i] not in duplicates:\n                duplicates.append(arr[i])\n    return duplicates",
        "language": "python"
    }'

# ============================================================================
# Test 5: Code Improvement
# ============================================================================

test_endpoint \
    "Test 5: Code Improvement" \
    "/review/improve" \
    '{
        "code": "def calc(x,y,op):\n    if op==\"+\":\n        return x+y\n    elif op==\"-\":\n        return x-y\n    elif op==\"*\":\n        return x*y\n    elif op==\"/\":\n        return x/y",
        "language": "python"
    }'

# ============================================================================
# Test 6: Diff Review (simple addition)
# ============================================================================

test_endpoint \
    "Test 6: Diff Review" \
    "/review/diff" \
    '{
        "diff": "diff --git a/app.py b/app.py\nindex 1234567..abcdefg 100644\n--- a/app.py\n+++ b/app.py\n@@ -1,3 +1,5 @@\n def hello():\n-    print(\"Hello\")\n+    name = input(\"Enter name: \")\n+    print(f\"Hello {name}\")\n+    return name"
    }'

# ============================================================================
# Test 7: Complex TypeScript with Multiple Issues
# ============================================================================

test_endpoint \
    "Test 7: Complex TypeScript" \
    "/review" \
    '{
        "code": "async function processData(data: any) {\n  const result = await fetch(\"https://api.example.com/\" + data.id);\n  const json = result.json();\n  console.log(json);\n  return json;\n}",
        "language": "typescript"
    }'

# ============================================================================
# Test 8: Security-Focused Review
# ============================================================================

test_endpoint \
    "Test 8: Security-Focused Review" \
    "/review" \
    '{
        "code": "const password = \"admin123\";\nfunction login(user, pass) {\n  if (pass === password) {\n    return true;\n  }\n  return false;\n}",
        "language": "javascript",
        "criteria": ["security_focused"]
    }'

# ============================================================================
# Summary
# ============================================================================

echo "=================================="
echo "Test Summary"
echo "=================================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
