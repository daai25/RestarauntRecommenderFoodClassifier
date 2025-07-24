from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO
import os
import pandas as pd
from PIL import Image
import requests
import shutil
import streamlit as st
from surprise import Dataset, Reader, SVD
from urllib.parse import urljoin

def Predict(images_bytes):
    """
    Processes a list of image byte objects, resizes them to 512x512, and saves them 
    as JPEGs in the 'images' folder for classification.

    Args:
        images_bytes (List[bytes]): List of image data in bytes.

    Returns:
        str: Summary message indicating the number of images processed.
    """
    output_dir = "images"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    for count, img_bytes in enumerate(images_bytes):
        pilImage = Image.open(BytesIO(img_bytes))
        pilImage = pilImage.convert("RGB")
        pilImage = pilImage.resize((512, 512), Image.LANCZOS)
        pilImage.save(os.path.join(output_dir, f"{count}.jpg"), format="JPEG", quality=85)

    #CallFunction(output_dir)
    return f"Processed {len(images_bytes)} images."

def ScrapeImagesFromUrl(url):
    """
    Takes a single URL, scrapes images, and returns them as a list of image byte objects.
    
    Args:
        url (str): The webpage URL to scrape for images.

    Returns:
        List[bytes]: List of image byte data from the page after resizing and conversion.
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
    """
    Generates the Streamlit tab for image classification, allowing users to either
    upload local image files or provide a URL to scrape images.
    """
    st.title("Image Classifier - Upload or Scrape")

    # User selects mode
    mode = st.radio("Choose Input Method:", ["Upload Images", "Submit Link"])
    
    if mode == "Upload Images":
        uploaded_files = st.file_uploader("Upload one or more images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        
        if uploaded_files:
            image_bytes = [file.read() for file in uploaded_files]
            result = Predict(image_bytes)
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
    """
    Generates the Streamlit tab for the restaurant recommender system.
    Allows users to review restaurants and receive personalized recommendations
    using an SVD model trained on all known user reviews.
    """
    def Recommender(user_id, csv_path="combined_reviews.csv"):
        """
        Recommends a new restaurant for the given user by training an SVD model
        on the full review dataset.

        Args:
            user_id (str): The user's ID (username).
            csv_path (str): Path to the review CSV file.

        Returns:
            str: The recommended restaurant name.
        """
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
        """
        Loads restaurant review data and returns the DataFrame and sorted list of unique names.

        Args:
            csv_path (str): Path to the CSV file.

        Returns:
            Tuple[pd.DataFrame, List[str]]: DataFrame of reviews, and list of restaurant names.
        """
        df = pd.read_csv(csv_path, delimiter="|")
        return df, sorted(df["restaurantName"].drop_duplicates())
    
    def append_review_to_csv(csv_path, restaurant, user_id, rating):
        """
        Appends a new review to the CSV file if the user hasn't already reviewed the restaurant.

        Args:
            csv_path (str): Path to the review CSV.
            restaurant (str): Name of the restaurant.
            user_id (str): ID of the reviewer.
            rating (int): Rating given by the user.

        Returns:
            bool: True if the review was added, False if it already existed.
        """
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

