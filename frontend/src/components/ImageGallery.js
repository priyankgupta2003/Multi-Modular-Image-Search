import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ImageGallery({ searchQuery }) {
  const [images, setImages] = useState([]);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const url = searchQuery
          ? `http://localhost:5000/api/images/search?query=${searchQuery}`
          : 'http://localhost:5000/api/images';
        const response = await axios.get(url);
        setImages(response.data);
      } catch (error) {
        console.error('Error fetching images:', error);
      }
    };

    fetchImages();
  }, [searchQuery]);

  return (
    <div className="image-gallery">
      {images.map((image) => (
        <div key={image._id} className="image-card">
          <img src={image.url} alt={image.title} />
          <h3>{image.title}</h3>
          <p>{image.description}</p>
          <p>Tags: {image.tags.join(', ')}</p>
        </div>
      ))}
    </div>
  );
}

export default ImageGallery;
