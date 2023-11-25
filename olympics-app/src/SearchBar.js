import React, { useState } from 'react';

function SearchBar({ onSearchSubmit}) {
  const [searchTerm, setSearchTerm] = useState('');

  const handleInputChange = (event) => {
    setSearchTerm(event.target.value);
    if (onSearchSubmit) {
      onSearchSubmit(event.target.value);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault(); // Prevents the default form submission behavior
    if (onSearchSubmit) {
      onSearchSubmit(searchTerm);
    }
  };


  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Search..."
        value={searchTerm}
        onChange={handleInputChange}
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;
