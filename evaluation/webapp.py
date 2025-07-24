from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO
import pandas as pd
from PIL import Image
import requests
import streamlit as st
from surprise import Dataset, Reader, SVD
from urllib.parse import urljoin

def Predict(images):
    return f"Processed {len(images)} images."

def ScrapeImagesFromUrl(url):
    """
    Takes a single URL, scrapes images, and returns them as a list of image byte objects.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")
    images_bytes_list = []

    for img_tag in img_tags:
        src = img_tag.get("src") or img_tag.get("data-src")
        if not src:
            continue

        if src.startswith("data:"):
            continue

        img_url = urljoin(url, src)

        try:
            img_response = requests.get(img_url, timeout=10)
            img_response.raise_for_status()

            # Open image using PIL to validate & optionally preprocess
            image = Image.open(BytesIO(img_response.content))
            image = image.convert("RGB")
            image = image.resize((512, 512), Image.LANCZOS)

            # Save image to bytes
            byte_stream = BytesIO()
            image.save(byte_stream, format="JPEG", quality=85)
            images_bytes_list.append(byte_stream.getvalue())

        except Exception as e:
            continue  # Skip images that fail to download or process

    return images_bytes_list

def GenerateClassifierTab():
    st.title("Image Classifier - Upload or Scrape")

    # User selects mode
    mode = st.radio("Choose Input Method:", ["Upload Images", "Submit Link"])
    
    if mode == "Upload Images":
        uploaded_files = st.file_uploader("Upload one or more images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
        if uploaded_files:
            result = Predict(uploaded_files)
            st.success(result)
    
    elif mode == "Submit Link":     
        url_input = st.text_input("Enter a URL to scrape images from")
    
        if st.button("Scrape and Process"):
            scraped_images_bytes = ScrapeImagesFromUrl(url_input)
            if len(scraped_images_bytes) > 0:
                result = Predict(scraped_images_bytes)
                st.success(result)
            else:
                st.error("Found no images at URL")
def GenerateRecommenderTab():
    def Recommender(user_id, csv_path="combined_reviews.csv"):
        df = pd.read_csv(csv_path, delimiter="|")
        df = df.rename(columns={
            "restaurantName": "item",
            "reviewerId": "user",
            "rating": "rating"
        })

        # Prepare surprise dataset
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[["user", "item", "rating"]], reader)
        trainset = data.build_full_trainset()

        # Train SVD model
        model = SVD()
        model.fit(trainset)

        # Find restaurants the user hasn't reviewed yet
        all_items = df["item"].unique()
        reviewed = df[df["user"] == user_id]["item"].unique()
        not_reviewed = [item for item in all_items if item not in reviewed]

        if not not_reviewed:
            return "You've reviewed everything!"

        # Predict ratings for unreviewed items
        predictions = [(item, model.predict(user_id, item).est) for item in not_reviewed]
        predictions.sort(key=lambda x: x[1], reverse=True)

        return predictions[0][0]  # Return top predicted restaurant

    # Load CSV at app start
    @st.cache_data
    def load_restaurant_data(csv_path):
        df = pd.read_csv(csv_path, delimiter="|")
        return df, sorted(df["restaurantName"].drop_duplicates())
    
    def append_review_to_csv(csv_path, restaurant, user_id, rating):
        df = pd.read_csv(csv_path, delimiter="|")
        already_reviewed = not df[(df["restaurantName"] == restaurant) & (df["reviewerId"] == user_id)].empty
    
        if already_reviewed:
            return False  # Skip writing
        today = datetime.today().strftime('%Y-%m-%d')
        new_row = f"{restaurant}|{user_id}|{rating}|{today},\n"

        with open(csv_path, "a", encoding="utf-8") as f:
            f.write(new_row)
        return True
        

    df_reviews, restaurant_names = load_restaurant_data("combined_reviews.csv")
    
    # RECOMMENDER TAB
    st.title("Recommender System")

    # Simple login
    username = st.text_input("Enter your username to get started:")
    if username:
        user_reviews_df = df_reviews[df_reviews["reviewerId"] == username][["restaurantName", "rating"]]

        if not user_reviews_df.empty:
            st.subheader("Your Reviews")
            st.table(user_reviews_df.rename(columns={"restaurantName": "Restaurant", "rating": "Rating"}))
        else:
            st.info("You haven't reviewed any restaurants yet.")

        # Review interface
        st.header("Submit a Review")

        restaurant_choice = st.selectbox("Select a restaurant to review:", restaurant_names)
        rating_choice = st.slider("Your rating:", 1, 5, 3)

        if st.button("Submit Review"):
            added = append_review_to_csv("combined_reviews.csv", restaurant_choice, username, rating_choice)

            if added:
                st.success(f"Review added for {restaurant_choice}")
                st.cache_data.clear()
                st.rerun()
            else:
                st.warning(f"You've already reviewed {restaurant_choice}")

        # Recommendation logic
        if len(user_reviews_df) >= 2:
            recommended = Recommender(username)
            st.header("Recommended Restaurant")
            st.success(f"We recommend you try: **{recommended}**")
        else:
            st.warning("Please review at least **two restaurants** to get a recommendation.")

st.set_page_config(
    page_title="Forkcast",
    page_icon="favicon.png",
    layout="wide",
)

st.image("ForkCast.png", width=200)

classifierTab, recommenderTab = st.tabs(["Image Classifier", "Recommender"])

with classifierTab:
    GenerateClassifierTab()

with recommenderTab:
    GenerateRecommenderTab()

