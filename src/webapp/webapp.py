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
from urllib.parse import urlparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
import src.main_classifier as main_classifier


def Predict(images_bytes):
    """
    Processes a list of image byte objects, resizes them to 512x512, and saves them
    as JPEGs in the 'images' folder for classification.

    Args:
        images_bytes (List[bytes]): List of image data in bytes.

    Returns:
        str: Summary message indicating the number of images processed.
    """
    output_dir = "images_to_classify"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    for count, img_bytes in enumerate(images_bytes):
        pilImage = Image.open(BytesIO(img_bytes))
        pilImage = pilImage.convert("RGB")
        pilImage = pilImage.resize((512, 512), Image.LANCZOS)
        pilImage.save(
            os.path.join(output_dir, f"{count}.jpg"), format="JPEG", quality=85
        )

    top_results = main_classifier.classify_restaurant(output_dir)
    filtered_results = [str(r) for r in top_results if r is not None]
    return f"Your top three recommendations are {', '.join(filtered_results)}."


def ScrapeImagesFromUrl(start_url, max_depth=1, max_pages=10):
    """
    Crawl `start_url` (and its sub-pages) for images with limits and progress tracking.
    """
    import time
    import random

    # Show progress to user
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Initializing crawler...")

    parsed_root = urlparse(start_url)
    visited = set()
    to_visit = [(start_url, 0)]
    images_bytes_list = []
    pages_visited = 0

    # Track domains to avoid going too far
    base_domain = ".".join(
        parsed_root.netloc.split(".")[-2:]
    )  # Get example.com from subdomain.example.com

    while to_visit and pages_visited < max_pages:
        current_url, depth = to_visit.pop(0)
        if current_url in visited or depth > max_depth:
            continue

        visited.add(current_url)
        pages_visited += 1

        # Update progress
        progress = min(pages_visited / max_pages, 1.0)
        progress_bar.progress(progress)
        status_text.text(f"Crawling page {pages_visited}/{max_pages}: {current_url}")

        # Add delay between requests
        time.sleep(random.uniform(0.1, 0.3))

        try:
            resp = requests.get(current_url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            status_text.text(f"Error accessing {current_url}: {str(e)}")
            time.sleep(1)  # Brief pause after error
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Process images with delay
        for img_tag in soup.find_all("img"):
            src = img_tag.get("src") or img_tag.get("data-src")
            if not src or src.startswith("data:"):
                continue

            img_url = urljoin(current_url, src)

            try:
                # Small delay between image requests
                time.sleep(random.uniform(0.1, 0.3))

                status_text.text(f"Downloading image: {img_url}")
                imr = requests.get(img_url, timeout=10)
                imr.raise_for_status()

                img = Image.open(BytesIO(imr.content)).convert("RGB")
                img = img.resize((512, 512), Image.LANCZOS)
                bs = BytesIO()
                img.save(bs, format="JPEG", quality=85)
                images_bytes_list.append(bs.getvalue())

                # Update on successful image download
                status_text.text(f"Downloaded {len(images_bytes_list)} images so far")

            except Exception as e:
                continue

        # More selective link crawling
        new_links = []
        for a in soup.find_all("a", href=True):
            link = urljoin(current_url, a["href"])
            p = urlparse(link)

            # Stricter domain filtering - must be same domain or subdomain
            link_domain = ".".join(p.netloc.split(".")[-2:])
            if link_domain == base_domain and link not in visited:
                new_links.append((link, depth + 1))

        # Limit links to avoid explosion
        random.shuffle(new_links)  # Randomize for better coverage
        to_visit.extend(new_links[:10])  # Add max 10 new links per page

    # Clean up progress indicators
    progress_bar.empty()
    status_text.text(f"Completed! Found {len(images_bytes_list)} images.")

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
        uploaded_files = st.file_uploader(
            "Upload one or more images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
        )

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
        df = df.rename(
            columns={"restaurantName": "item", "reviewerId": "user", "rating": "rating"}
        )

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
        predictions = [
            (item, model.predict(user_id, item).est) for item in not_reviewed
        ]
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
        already_reviewed = not df[
            (df["restaurantName"] == restaurant) & (df["reviewerId"] == user_id)
        ].empty

        if already_reviewed:
            return False  # Skip writing
        today = datetime.today().strftime("%Y-%m-%d")
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
        user_reviews_df = df_reviews[df_reviews["reviewerId"] == username][
            ["restaurantName", "rating"]
        ]

        if not user_reviews_df.empty:
            st.subheader("Your Reviews")
            st.table(
                user_reviews_df.rename(
                    columns={"restaurantName": "Restaurant", "rating": "Rating"}
                )
            )
        else:
            st.info("You haven't reviewed any restaurants yet.")

        # Review interface
        st.header("Submit a Review")

        restaurant_choice = st.selectbox(
            "Select a restaurant to review:", restaurant_names
        )
        rating_choice = st.slider("Your rating:", 1, 5, 3)

        if st.button("Submit Review"):
            added = append_review_to_csv(
                "combined_reviews.csv", restaurant_choice, username, rating_choice
            )

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
            st.warning(
                "Please review at least **two restaurants** to get a recommendation."
            )


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
