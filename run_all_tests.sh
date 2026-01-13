#!/bin/bash
# Master test runner - runs all tests

echo "=========================================="
echo "Running All Tests (Backend + Worker + Frontend)"
echo "=========================================="

FAILED=0

# Run backend tests
echo ""
echo "1/3 Backend Tests..."
cd backend
bash run_tests.sh
if [ $? -ne 0 ]; then
    FAILED=1
fi
cd ..

# Run worker tests
echo ""
echo "2/3 Worker Tests..."
cd worker
bash run_tests.sh
if [ $? -ne 0 ]; then
    FAILED=1
fi
cd ..

# Run frontend tests
echo ""
echo "3/3 Frontend Tests..."
cd frontend
npm test -- --run
if [ $? -ne 0 ]; then
    FAILED=1
fi
cd ..

# Final result
echo ""
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ All test suites passed!"
else
    echo "❌ Some test suites failed!"
    exit 1
fi
echo "=========================================="
