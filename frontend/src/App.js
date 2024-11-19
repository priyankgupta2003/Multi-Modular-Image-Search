import React, { useState } from 'react';
import ImageGallery from './components/ImageGallery';
import SearchBar from './components/SearchBar';
import UploadForm from './components/UploadForm';
import './App.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Image Gallery</h1>
      </header>
      <main>
        <SearchBar onSearch={handleSearch} />
        <UploadForm />
        <ImageGallery searchQuery={searchQuery} />
      </main>
    </div>
  );
}

export default App;
