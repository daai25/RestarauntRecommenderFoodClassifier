# this script will run all tests in the project
cd ..

# printing the current directory for debugging
echo "Current directory: $(pwd)\n"
echo "Running URL-Finder tests..."
python3 -m pytest test/url_finder/url_finder_test.py -s

echo "URL-Finder tests completed."
echo "\n\nRunning Image-Filter tests..."
python3 -m pytest test/image_filter/image_filter_test.py -s