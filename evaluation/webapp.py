from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO
import pandas as pd
from PIL import Image
import requests
import streamlit as st
from urllib.parse import urljoin

# Simulated Magic() and TurboScraper()
def Magic(list_of_image_bytes):
    return f"Processed {len(list_of_image_bytes)} images."


def TurboScraper(url):
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
            images_bytes = [file.read() for file in uploaded_files]
    
            # Optionally preview images
            for img in images_bytes:
                st.image(img, use_container_width=True)
    
            # Process with Magic()
            result = Magic(images_bytes)
            st.success(result)
    
    elif mode == "Submit Link":     
        url_input = st.text_input("Enter a URL to scrape images from")
    
        if url_input:
            if st.button("Scrape and Process"):
                scraped_images_bytes = TurboScraper(url_input)
                for img_bytes in scraped_images_bytes:
                        st.image(img_bytes, use_container_width=True)
                result = Magic(scraped_images_bytes)
                st.success(result)

def GenerateRecommenderTab():
    def Recommender(user_reviews):
    # Recommend the restaurant with fewest user reviews as dummy logic
        reviewed_names = set(r for r, _ in user_reviews)
        remaining = [r for r in restaurant_names if r not in reviewed_names]
        return remaining[0] if remaining else "You've reviewed everything!"

    # Load CSV at app start
    @st.cache_data
    def load_restaurant_data(csv_path):
        df = pd.read_csv(csv_path, delimiter="|")
        return df, sorted(df["restaurantName"].drop_duplicates())
    
    def append_review_to_csv(csv_path, restaurant, user_id, rating):
        today = datetime.today().strftime('%Y-%m-%d')
        new_row = f"{restaurant}|{user_id}|{rating}|{today},\n"

        with open(csv_path, "a", encoding="utf-8") as f:
            f.write(new_row)

    df_reviews, restaurant_names = load_restaurant_data("combined_reviews.csv")
    
    # RECOMMENDER TAB
    st.title("Recommender System")

    # Simple login
    username = st.text_input("Enter your username to get started:")
    if username:
        if f"{username}_reviews" not in st.session_state:
            user_df = df_reviews[df_reviews["reviewerId"] == username][["restaurantName", "rating"]]
            st.session_state[f"{username}_reviews"] = list(user_df.itertuples(index=False, name=None))

        # From now on, same logic as before:

        # Review interface
        st.header("Submit a Review")

        restaurant_choice = st.selectbox("Select a restaurant to review:", restaurant_names)
        rating_choice = st.slider("Your rating:", 1, 5, 3)

        if st.button("Submit Review"):
            reviews = st.session_state[f"{username}_reviews"]
            reviews_dict = dict(reviews)
            reviews_dict[restaurant_choice] = rating_choice
            st.session_state[f"{username}_reviews"] = list(reviews_dict.items())
        
            # Append to CSV (optionally skip if it's a duplicate)
            append_review_to_csv("combined_reviews.csv", restaurant_choice, username, rating_choice)
            st.success(f"Review added for {restaurant_choice}")

        # Show existing reviews
        user_reviews = st.session_state[f"{username}_reviews"]
        if user_reviews:
            st.subheader("Your Reviews")
            st.table(pd.DataFrame(user_reviews, columns=["Restaurant", "Rating"]))
        else:
            st.info("You haven't reviewed any restaurants yet.")

        # Recommendation logic
        if len(user_reviews) >= 2:
            recommended = Recommender(user_reviews)
            st.header("Recommended Restaurant")
            st.success(f"We recommend you try: **{recommended}**")
        else:
            st.warning("Please review at least **two restaurants** to get a recommendation.")

# Streamlit App
st.set_page_config(
    layout="wide"
)
classifierTab, recommenderTab = st.tabs(["Image Classifier", "Recommender"])

with classifierTab:
    GenerateClassifierTab()

with recommenderTab:
    GenerateRecommenderTab()

