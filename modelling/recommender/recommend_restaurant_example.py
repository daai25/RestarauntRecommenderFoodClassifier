import pandas as pd
import os
from surprise import Dataset, Reader, dump

# Load model
base_dir = os.path.dirname(os.path.abspath(__file__))
_, model = dump.load(os.path.join(base_dir, 'restaurant_recommender.pkl'))

# Load csv dataset
df = pd.read_csv(os.path.join(base_dir, 'combined_reviews.csv'), delimiter='|')
reader = Reader(rating_scale=(1, 5))

# Load dataset from DataFrame
data = Dataset.load_from_df(df[['reviewerId', 'restaurantName', 'rating']], reader)

# Example input: Simulated new user reviews
new_user_id = 'Lorino75' # New unique user ID

new_user_reviews = [
    #(new_user_id, 'Typisch Thai', 4),
    (new_user_id, 'Palmera', 2),
    (new_user_id, 'National', 1),
    (new_user_id, 'Wintialp', 3),
    (new_user_id, 'Cafe Restaurant Obergass', 4),
    (new_user_id, 'Club zur Geduld', 5)
]

# Identify restaurants this user hasn't rated
all_restaurants = df['restaurantName'].unique()
reviewed_restaurants = {iid for uid, iid, rating in new_user_reviews}
restaurants_to_recommend = [iid for iid in all_restaurants if iid not in reviewed_restaurants]

# Predict ratings for all unseen restaurants
predictions = []
for restaurant_id in restaurants_to_recommend:
    pred = model.predict(new_user_id, restaurant_id)
    predictions.append((restaurant_id, pred.est))

# Sort by predicted rating
predictions.sort(key=lambda x: x[1], reverse=True)

# Recommend top 3 restaurants
top_n = 3
recommended_restaurants = predictions[:top_n]

# Show results
for rest_id, rating in recommended_restaurants:
    print(f"Recommend Restaurant ID: {rest_id} with predicted rating {rating:.2f}")
