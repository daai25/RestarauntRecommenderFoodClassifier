"""
This file is not actually used, and is just here for storing some of the steps I took to get the recommender working.
This should not be run, but may be as a proof of concept.
"""

import os
import pandas as pd
from surprise import Dataset, Reader, dump, SVD, accuracy
from surprise.model_selection import train_test_split, cross_validate, GridSearchCV

# Load the uploaded CSV file
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "combined_reviews.csv")
df = pd.read_csv(file_path)

# The CSV uses | as the delimiter so read it like that
df = pd.read_csv(file_path, sep="|")

# Rename columns
df.columns = ["restaurant", "user", "rating", "date"]

#Reader that lets us look at the dataframe as a user ==> Item ==> Value (rating) relationship
reader = Reader(rating_scale=(1,5))
data = Dataset.load_from_df(df[["user", "restaurant", "rating"]], reader)

trainset, testset = train_test_split(data, test_size=0.2)


#_, model = dump.load('restaurant_recommender.pkl')




# Build and train
#algo_options ={
#    "name": "cosine",
#    "user_based": True,
#}

#algorithm = SVD(n_factors=150, lr_all=0.01, reg_all=0.05, n_epochs=40)
#
#
#algorithm.fit(trainset)
#model_name = 'restaurant_recommender.pkl'
#dump.dump(file_name = model_name, algo = algorithm)





#==> This is how I landed on the conclusion that the best we can get is 0.9889 RMSE with parameters {'n_factors': 150, 'lr_all': 0.01, 'reg_all': 0.05}
param_grid = {
    'n_factors': [50, 100, 150],
    'lr_all': [0.002, 0.005, 0.01],
    'reg_all': [0.02, 0.05, 0.1]
}

gs = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=5)
gs.fit(data)

print("Best RMSE score:", gs.best_score['rmse'])
print("Best parameters:", gs.best_params['rmse'])

# Best model
algo = gs.best_estimator['rmse']
algo.fit(trainset)
# Predict on test set
predictions = algo.test(testset)
print("RMSE:", accuracy.rmse(predictions)) #Usually around 1, so it's not good, but not totally random
