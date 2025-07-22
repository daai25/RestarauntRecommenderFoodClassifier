# this script will run all tests in the project
cd ..

# Detect OS
OS_TYPE="$(uname)"
echo "Detected OS: $OS_TYPE"

# printing the current directory for debugging
echo "Current directory: $(pwd)\n"

if [ "$OS_TYPE" = "Darwin" ]; then
    echo "Running tests on macOS..."
    PYTHON_CMD="python3"
elif [ "$OS_TYPE" = "Linux" ]; then
    echo "Running tests on Linux..."
    PYTHON_CMD="python3"
elif [[ "$OS_TYPE" == MINGW* || "$OS_TYPE" == CYGWIN* || "$OS_TYPE" == MSYS* ]]; then
    echo "Running tests on Windows..."
    PYTHON_CMD="python"
else
    echo "Unknown OS, defaulting to python3"
    PYTHON_CMD="python3"
fi

echo "Running URL-Finder tests..."
$PYTHON_CMD -m pytest test/url_finder/url_finder_test.py -s

echo "URL-Finder tests completed."
echo "\n\nRunning Image-Filter tests..."
$PYTHON_CMD -m pytest test/image_filter/image_filter_test.py -s