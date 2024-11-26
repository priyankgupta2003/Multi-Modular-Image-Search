import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Configure API endpoint
API_BASE_URL = "http://localhost:8999"

# Page config
st.set_page_config(page_title="Image Search Engine", layout="wide")

def display_s3_image(s3_url):
    try:
        # For LocalStack, replace the endpoint URL
        s3_url = s3_url.replace("https://s3.amazonaws.com", "http://localhost:4566")
        
        response = requests.get(s3_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            return image
        else:
            st.error(f"Failed to load image: HTTP {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None

def search_by_text(query: str):
    response = requests.post(f"{API_BASE_URL}/images/search/text", params={"query": query})
    return response.json()

def search_by_url(image_url: str):
    response = requests.post(f"{API_BASE_URL}/image/search/url/", params={"image_url": image_url})
    return response.json()

def search_by_image(image_file):
    files = {"image": image_file}
    response = requests.post(f"{API_BASE_URL}/images/search/image/", files=files)
    return response.json()

def add_image(image_url: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/images/add",
            params={"image_url": image_url}
        )
        if response.status_code == 422:
            st.error("Invalid image URL format")
            return None
        return response.json()
    except Exception as e:
        st.error(f"Error adding image: {str(e)}")
        return None

def get_all_images():
    response = requests.get(f"{API_BASE_URL}/images/list")
    return response.json()

def delete_image(image_id: str):
    response = requests.delete(f"{API_BASE_URL}/images/delete", params={"image_id": image_id})
    return response.json()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Search", "Add Image", "Image Gallery"])

if page == "Search":
    st.title("Image Search")
    
    search_method = st.radio("Search Method", ["Text", "URL", "Image Upload"])
    
    if search_method == "Text":
        query = st.text_input("Enter search query")
        if st.button("Search"):
            if query:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/images/search/text",
                        params={"query": query}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("results") and len(data["results"]) > 0:
                            for result in data["results"]:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    # Convert S3 URL to LocalStack format
                                    s3_url = result.get("s3_url", "")
                                    if s3_url:
                                        localstack_url = s3_url.replace(
                                            "https://s3.amazonaws.com",
                                            "http://localhost:4566"
                                        )
                                        try:
                                            response = requests.get(localstack_url)
                                            if response.status_code == 200:
                                                image = Image.open(BytesIO(response.content))
                                                st.image(image)
                                        except Exception as e:
                                            st.error(f"Error loading image: {str(e)}")
                                with col2:
                                    st.write(f"Similarity: {result.get('similarity_score', 0)}%")
                        else:
                            st.warning("No results found")
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Search error: {str(e)}")

    elif search_method == "URL":
        image_url = st.text_input("Enter image URL")
        if st.button("Search"):
            if image_url:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/image/search/url/",
                        params={"image_url": image_url}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("results"):
                            for result in data["results"]:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    s3_url = result.get("s3_url", "")
                                    if s3_url:
                                        localstack_url = s3_url.replace(
                                            "https://s3.amazonaws.com",
                                            "http://localhost:4566"
                                        )
                                        try:
                                            img_response = requests.get(localstack_url)
                                            if img_response.status_code == 200:
                                                image = Image.open(BytesIO(img_response.content))
                                                st.image(image)
                                        except Exception as e:
                                            st.error(f"Error loading image: {str(e)}")
                                with col2:
                                    st.write(f"Similarity: {result.get('similarity_score', 0)}%")
                        else:
                            st.warning("No results found")
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Search error: {str(e)}")

    else:  # Image Upload
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_file and st.button("Search"):
            try:
                files = {"image": uploaded_file}
                response = requests.post(
                    f"{API_BASE_URL}/images/search/image/",
                    files=files
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("results"):
                        for result in data["results"]:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                s3_url = result.get("s3_url", "")
                                if s3_url:
                                    localstack_url = s3_url.replace(
                                        "https://s3.amazonaws.com",
                                        "http://localhost:4566"
                                    )
                                    try:
                                        img_response = requests.get(localstack_url)
                                        if img_response.status_code == 200:
                                            image = Image.open(BytesIO(img_response.content))
                                            st.image(image)
                                    except Exception as e:
                                        st.error(f"Error loading image: {str(e)}")
                            with col2:
                                st.write(f"Similarity: {result.get('similarity_score', 0)}%")
                    else:
                        st.warning("No results found")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Search error: {str(e)}")

elif page == "Add Image":
    st.title("Add New Image")
    image_url = st.text_input("Enter image URL")
    if st.button("Add Image"):
        if image_url:
            try:
                result = add_image(image_url)
                if isinstance(result, dict) and result.get("status") == "success":
                    st.success(f"Image added successfully! ID: {result['image_id']}")
                else:
                    st.error("Failed to add image")
            except Exception as e:
                st.error(f"Error adding image: {str(e)}")

else:  # Image Gallery
    st.title("Image Gallery")
    results = get_all_images()
    
    if results["status"] == "success":
        for i in range(0, len(results["images"]), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(results["images"]):
                    image = results["images"][i + j]
                    with cols[j]:
                        st.image(image["s3_link"])  # Changed from s3_url to s3_link
                        if st.button(f"Delete", key=image["id"]):
                            delete_result = delete_image(image["id"])
                            if delete_result["status"] == "success":
                                st.success("Image deleted successfully!")
                                st.rerun()