import os


if __name__ == "__main__":
    # food or not food dataset archive with training and testing data
    train_dir = "C:/nfr/food_or_not_food/archive/food_data/train"
    test_dir = "C:/nfr/food_or_not_food/archive/food_data/test"

    # check if the directories exist and exit the program
    if not os.path.exists(train_dir):
        print(f"Training directory {train_dir} does not exist.")
        exit(1)
    if not os.path.exists(test_dir):
        print(f"Testing directory {test_dir} does not exist.")
        exit(1)

