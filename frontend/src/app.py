import streamlit as st
import requests
import io
from PIL import Image
import os
from urllib.parse import urljoin

# Configure the API base URL
API_BASE_URL = "http://localhost:8999"

st.set_page_config(
    page_title="Image Search Gallery",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .gallery-image {
        width: 100%;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .search-results {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 20px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def get_s3_image_url(s3_path):
    """Convert S3 path to public URL"""
    if not s3_path:
        return None
    
    # Remove 's3://' prefix and split into bucket and key
    path = s3_path.replace('s3://', '')
    parts = path.split('/')
    bucket = parts[0]
    key = '/'.join(parts[1:])
    
    # Replace with your AWS region
    region = "your-region"
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

def display_image_card(image_data):
    """Display an image card with metadata"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        image_url = get_s3_image_url(image_data.get('s3_path') or image_data.get('url'))
        if image_url:
            try:
                st.image(image_url, use_column_width=True)
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
    
    with col2:
        if image_data.get('title'):
            st.subheader(image_data['title'])
        if image_data.get('description'):
            st.write(image_data['description'])
        if image_data.get('tags'):
            tags = image_data['tags']
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',')]
            st.write("Tags:", ", ".join(tags))
        if image_data.get('similarity_score'):
            score = float(image_data['similarity_score']) * 100
            st.progress(score/100)
            st.write(f"Similarity: {score:.2f}%")

def main():
    st.title("Image Search Gallery")
    
    # Sidebar for search options
    st.sidebar.title("Search Options")
    search_option = st.sidebar.radio(
        "Choose search method:",
        ["Browse All", "Text Search", "Image URL Search", "Upload Image"]
    )

    if search_option == "Browse All":
        try:
            response = requests.get(urljoin(API_BASE_URL, "/images/list"))
            if response.status_code == 200:
                images = response.json().get('images', [])
                if not images:
                    st.info("No images found in the gallery.")
                else:
                    for image in images:
                        display_image_card(image)
            else:
                st.error("Failed to fetch images from the server.")
        except Exception as e:
            st.error(f"Error connecting to the server: {str(e)}")

    elif search_option == "Text Search":
        query = st.text_input("Enter search terms:")
        if st.button("Search") and query:
            try:
                response = requests.post(
                    urljoin(API_BASE_URL, "/images/search/text"),
                    json={"query": query}
                )
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    if not results:
                        st.info("No matching images found.")
                    else:
                        for image in results:
                            display_image_card(image)
                else:
                    st.error("Search request failed.")
            except Exception as e:
                st.error(f"Error performing search: {str(e)}")

    elif search_option == "Image URL Search":
        image_url = st.text_input("Enter image URL:")
        if st.button("Search") and image_url:
            try:
                response = requests.post(
                    urljoin(API_BASE_URL, "/image/search/url/"),
                    json={"image_url": image_url}
                )
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    if not results:
                        st.info("No similar images found.")
                    else:
                        for image in results:
                            display_image_card(image)
                else:
                    st.error("Search request failed.")
            except Exception as e:
                st.error(f"Error performing search: {str(e)}")

    elif search_option == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image file:", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            try:
                files = {'image': uploaded_file}
                response = requests.post(
                    urljoin(API_BASE_URL, "/images/search/image/"),
                    files=files
                )
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    if not results:
                        st.info("No similar images found.")
                    else:
                        for image in results:
                            display_image_card(image)
                else:
                    st.error("Search request failed.")
            except Exception as e:
                st.error(f"Error performing search: {str(e)}")

if __name__ == "__main__":
    main()