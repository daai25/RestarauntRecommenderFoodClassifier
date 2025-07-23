import os
import pandas as pd
from surprise import Dataset, Reader, dump, SVD
from surprise.model_selection import train_test_split

'''
Trains a model based on the combined_reviews.csv file and saves it under restaurant_recommender.pkl.
Utilizes SVD and the Surprise library for training, as well as pandas for handling the CSV.
'''
# Load the uploaded CSV file
base_dir = os.path.dirname(os.path.abspath(__file__))
#file_path = os.path.join(base_dir, "combined_reviews.csv")
file_path = os.path.join(base_dir, "ungerdybungerdy.csv")
df = pd.read_csv(file_path, sep="|")

# Rename columns
df.columns = ["reviewerId", "restaurantName", "rating", "date"]

# Reader that lets us look at the dataframe as a user ==> Item ==> Value (rating) relationship
reader = Reader(rating_scale=(1,5))
data = Dataset.load_from_df(df[['reviewerId', 'restaurantName', 'rating']], reader)

trainset, testset = train_test_split(data, test_size=0.2)

# Build and train
algo_options ={
    "name": "cosine",
    "user_based": True,
}

algorithm = SVD(n_factors=150, lr_all=0.01, reg_all=0.05, n_epochs=40)
algorithm.fit(trainset)

# Save model
model_name = os.path.join(base_dir, 'restaurant_recommender.pkl')
dump.dump(file_name = model_name, algo = algorithm)
