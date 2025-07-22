# root/test/web_scraper/web_scraper_test.py
import os
import pytest
import src.web_scraper as web_scraper

_test_output_directory = os.path.join(os.path.dirname(__file__), "test_output")

def test_web_scraper():
    # check if the _test_output_directory exists
    assert (
        os.path.exists(_test_output_directory)
    ), f"Test output directory does not exist: {_test_output_directory}"

    clean_test_output_directory()

    # check if the output directory is clean and only .gitkeep is present
    for filename in os.listdir(_test_output_directory):
        if filename != ".gitkeep":
            raise AssertionError(
                f"Test output directory is not clean: {filename} found"
            )


    test_url = "http://localhost:8000/"
    scraper = web_scraper.ImageScraper()
    scraper.run([test_url], _test_output_directory, do_filter=False)

    # Expect images to be saved under test_output/localhost:8000/
    domain_folder = os.path.join(_test_output_directory, "localhost_8000")
    assert os.path.exists(domain_folder)
    files = os.listdir(domain_folder)
    # check if all files in the domain folder are images
    for file in files:
        assert (
            file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
        ), f"File {file} in {domain_folder} is not an image file."
    # check if there are 14 image files in the domain folder
    assert (
            len(files) == 14
    ), f"Expected 14 image files, but found {len(files)} files in {domain_folder}"

def clean_test_output_directory():
    """
    Clean the test output directory by removing all files and directories except .gitkeep.
    """
    for filename in os.listdir(_test_output_directory):
        file_path = os.path.join(_test_output_directory, filename)
        if filename != ".gitkeep":
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  # Remove empty directories

if __name__ == "__main__":
    pytest.main([__file__])