
# ForkCast
![ForkCast Logo](src/webapp/ForkCast.png)

## Restaurant Recommender and Cuisine Type Classifier

---

### Setup conda environment

**Install** conda environment:
```sh
$ conda env create -f conda.yml
```
**Update** the environment with new packages/versions:
1. modify template.yml
2. run `conda env update`:
```sh
$ conda env update --name restaurant-recommend-classifier --file conda.yml --prune
```
`prune` uninstalls dependencies which were removed from conda.yml

**Use** environment:
before working on the project always make sure you have the environment activated:
```sh
$ conda activate restaurant-recommend-classifier
```

**List** all installed environments:
From the base environment run
```sh
$ conda info --envs
```

**Remove** environment:
```sh
$ conda env remove -n restaurant-recommend-classifier
```

See the complete documentation on [managing conda-environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

---

### Project Structure

The Project is seperated in the following directories:

```text
RestarauntRecommenderFoodClassifier/
├── data_acquisition
├── docs
├── evaluation
├── modelling
├── scripts
├── src
└── test
```

#### data acquisition

[base: data_acquisition](https://github.com/daai25/RestarauntRecommenderFoodClassifier/tree/main/data_acquisition)

This directory contains all the scripts for our scraped data:
```text
data_acquisition/
├── open_street_map
├── restarauntContentScraper
└── user_reviews
```

- `open_street_map`: Contains a script to get all the restaurants information from **OpenStreetMap** and saves them in a JSON file.
  Additionally, it contains a mapping from food types to cuisine types, which is used by our cuisine type classifier. 
- `restarauntContenScraper`: Contains a web scraping spider which goes through all the **OpenStreetMap** collected
  restaurant web-links and downloads all the images including the raw HTML.
- `user_reviews`: Contains a script for getting additional Google reviews using their API.

#### docs

[base: docs](https://github.com/daai25/RestarauntRecommenderFoodClassifier/tree/main/docs)

Contains all the `.qmd` files, which are rendered in GitHub Pages as a Quarto documentation.

#### evaluation

[base: evaluation](https://github.com/daai25/RestarauntRecommenderFoodClassifier/tree/main/evaluation)

This directory the following two subdirectories:
```text
evaluation/
├── food_classifier
└── food_or_not_food
```
which includes test data, our trained models and a script to run the evaluation.
It also includes the already evaluated results, which are copied into scripts.

The evaluation scripts makes different plots of the results, which are already moved to the `docs`:
[docs/pics](https://github.com/daai25/RestarauntRecommenderFoodClassifier/tree/main/docs/pics)

#### modelling

[base: modelling](https://github.com/daai25/RestarauntRecommenderFoodClassifier/tree/main/modelling)

Includes the training scripts for food classifier, food or not food classifier and recommender:
```text
modelling/
├── food_classifier
├── food_or_not_food
└── recommender
```

`food_classifier`:
```text
modelling/food_classifier/
├── classifier_trainer.py
├── data_plot.py
├── data_prep.py
└── training_resnet50_logs.txt
```

- `classifier_trainer.py`: The training scripts.
- `data_plot.py`: Plotting scripts which plots the training process.
- `data_prep.py`: A script for making the training / validating / testing split.
- `training_resnet50_logs.txt`: Logs from the training process, which are copied into the `data_plot.py`.

`food_or_not_food`:
```text
modelling/food_or_not_food/
├── data_plot.py
├── dataset/
├── food_or_not_food_custom_model.py
├── food_or_not_food_resnet18_trainer.py
├── food_or_not_food_resnet50_trainer.py
├── training_resnet18_base_aug.txt
├── training_resnet18_base_no_aug.txt
├── training_resnet18_improved_aug.txt
└── training_resnet50_improved_aug.txt
```

- `data_plot.py`: Plots the training process.
- `dataset/`: The improved dataset which was used during for the training.
- `food_or_not_food_custom_model.py`: Contains a custom model, which was not used in the final product.
- `food_or_not_food_resnet18_trainer.py`: The resnet18 trainer script.
- `food_or_not_food_resnet50_trainer.py`: The resnet50 trainer script.

The remaining text data are all logs from the training.

`recommender`:
```text
modelling/recommender/
├── combined_reviews.csv
├── recommend_restaurant_example.py
├── restaurant_recommender.pkl
├── testfile.py
└── train_model.py
```

- `combined_reviews.csv`: The training data, which are reviews from Google and .
- `restaurant_recommender.pkl`: The saved / trained model.
- `testfile.py`: The testing script.
- `train_model.py`: The recommender training script.

#### scripts

[base: scripts](https://github.com/daai25/RestarauntRecommenderFoodClassifier/tree/main/scripts)

Containing different scripts.

Currently only includes a script to starting the tests in the `test` directory.

```
./scripts/run_test.sh
```

#### src

[base: src](https://github.com/daai25/RestarauntRecommenderFoodClassifier/tree/main/src)

Containing the web app and the different used packages,
for example: `image_filter` which has a simple framework for image filtering.

#### test

[base: test](https://github.com/daai25/RestarauntRecommenderFoodClassifier/tree/main/test)

The testing directory, which gets run be the testing script in `script`.
