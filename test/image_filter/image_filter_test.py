import os
import src.image_filter as image_filter

_test_images_directory = "test_images"

# these are the test images used for the image filter tests
_test_images = [
    "blurry (1) - Kopie.jpg",
    "blurry (1).jpg",
    "blurry (10) - Kopie.jpg",
    "blurry (10).jpg",
    "blurry (2) - Kopie.jpg",
    "blurry (2).jpg",
    "blurry (3) - Kopie.jpg",
    "blurry (3).jpg",
    "blurry (4) - Kopie.jpg",
    "blurry (4).jpg",
    "blurry (5) - Kopie.jpg",
    "blurry (5).jpg",
    "blurry (6) - Kopie.jpg",
    "blurry (6).jpg",
    "blurry (7) - Kopie.jpg",
    "blurry (7).jpg",
    "blurry (8) - Kopie.jpg",
    "blurry (8).jpg",
    "blurry (9) - Kopie.jpg",
    "blurry (9).jpg",
    "food (1).jpg",
    "food (1) - Kopie.jpg",
    "food (10).jpg",
    "food (2).jpg",
    "food (2) - Kopie.jpg",
    "food (3).jpg",
    "food (3) - Kopie.jpg",
    "food (4).jpg",
    "food (4) - Kopie.jpg",
    "food (5).jpg",
    "food (5) - Kopie.jpg",
    "food (6).jpg",
    "food (7).jpg",
    "food (8).jpg",
    "food (9).jpg",
    "not_food (1) - Kopie.jpg",
    "not_food (1).jpg",
    "not_food (10) - Kopie.jpg",
    "not_food (10).jpg",
    "not_food (2) - Kopie.jpg",
    "not_food (2).jpg",
    "not_food (3) - Kopie.jpg",
    "not_food (3).jpg",
    "not_food (4) - Kopie.jpg",
    "not_food (4).jpg",
    "not_food (5) - Kopie.jpg",
    "not_food (5).jpg",
    "not_food (6) - Kopie.jpg",
    "not_food (6).jpg",
    "not_food (7) - Kopie.jpg",
    "not_food (7).jpg",
    "not_food (8) - Kopie.jpg",
    "not_food (8).jpg",
    "not_food (9) - Kopie.jpg",
    "not_food (9).jpg",
    "uniform_white (1).png",
    "uniform_white (2).png",
    "uniform_white (3).png",
    "uniform_white (4).png",
    "uniform_white (5).png"
]

# Disclaimer: Copies of images are not included in this list,
# because we don't know which duplicated copy deleted.
_filter_images = [
    "blurry (1) - Kopie.jpg",
    "blurry (1).jpg",
    "blurry (10) - Kopie.jpg",
    "blurry (10).jpg",
    "blurry (2) - Kopie.jpg",
    "blurry (2).jpg",
    "blurry (3) - Kopie.jpg",
    "blurry (3).jpg",
    "blurry (4) - Kopie.jpg",
    "blurry (4).jpg",
    "blurry (5) - Kopie.jpg",
    "blurry (5).jpg",
    "blurry (6) - Kopie.jpg",
    "blurry (6).jpg",
    "blurry (7) - Kopie.jpg",
    "blurry (7).jpg",
    "blurry (8) - Kopie.jpg",
    "blurry (8).jpg",
    "blurry (9) - Kopie.jpg",
    "blurry (9).jpg",
    "not_food (1) - Kopie.jpg",
    "not_food (1).jpg",
    "not_food (10) - Kopie.jpg",
    "not_food (10).jpg",
    "not_food (2) - Kopie.jpg",
    "not_food (2).jpg",
    "not_food (3) - Kopie.jpg",
    "not_food (3).jpg",
    "not_food (4) - Kopie.jpg",
    "not_food (4).jpg",
    "not_food (5) - Kopie.jpg",
    "not_food (5).jpg",
    "not_food (6) - Kopie.jpg",
    "not_food (6).jpg",
    "not_food (7) - Kopie.jpg",
    "not_food (7).jpg",
    "not_food (8) - Kopie.jpg",
    "not_food (8).jpg",
    "not_food (9) - Kopie.jpg",
    "not_food (9).jpg",
    "uniform_white (1).png",
    "uniform_white (2).png",
    "uniform_white (3).png",
    "uniform_white (4).png",
    "uniform_white (5).png"
]

def test_image_filter():
    # check if all the images are included in the test images directory
    for image in _test_images:
        assert image in os.listdir(_test_images_directory), f"Image {image} not found in {_test_images_directory}"

    # create an instance of the FoodOrNotFoodImageFilter
    food_filter = image_filter.FoodOrNotImageFilter()

    # create an instance of the ImageFilter
    img_filter = image_filter.ImageFilter(filter_extensions=[food_filter])

    # filter the images in the test images directory
    stats = img_filter.filter_images(_test_images_directory, is_relative=True, delete=False)

    # assert if the total number of images is correct
    assert stats["total_images"] == len(_test_images), \
        f"Total number of images is incorrect: {stats['total_images']}"

    # assert if the number of blurry images is correct
    # it should detect 25 blurry images, 20 from blurry not food images and 5 from uniform images
    assert stats["total_blurry_images"] == 25, \
        f"Number of blurry images is incorrect: {stats['total_blurry_images']}"

    # assert if the number of uniform images is correct
    # no more images are detected as uniform images, because it was already detected as blurry images
    assert stats["total_uniform_images"] == 0, \
        f"Number of uniform images is incorrect: {stats['total_uniform_images']}"

    # assert if the number of duplicate images is correct
    # it should detect 15 duplicated images, 10 from not food and 5 from food images
    assert stats["total_duplicate_images"] == 15, \
        f"Number of duplicate images is incorrect: {stats['total_duplicate_images']}"

    # assert if the errors were correctly captured and if the number of errors is zero
    assert stats["num_of_errors"] == len(stats["captured_errors"]), f"Errors were not captured correctly: {stats['captured_errors']}"
    assert stats["num_of_errors"] == 0, f"Errors were captured: {stats['captured_errors']}"

    # assert if the number of filtered images is correct
    assert stats["total_filtered"][food_filter.__class__.__name__] == 10, \
        f"Number of filtered images is incorrect: {stats['total_filtered'][food_filter.__class__.__name__]}"

    # check if at least all the images_paths are included in the filtered image paths
    for image in _filter_images:
        image = os.path.join(_test_images_directory, image)
        found = False
        for filtered_image in stats["filtered_image_paths"]:
            if image == filtered_image:
                found = True
                break

        assert found, f"Image {image} is not filtered correctly, it is still in the filtered image paths"

    # check if the number of valid images is correct
    assert stats["total_valid_images"] == 10, \
        f"Number of valid images is incorrect: {stats['total_valid_images']}"
