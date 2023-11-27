import React from 'react';

function SearchBar({ onSearchSubmit }) {
  let searchTerm = '';

  const handleInputChange = (event) => {
    searchTerm = event.target.value;
    if (onSearchSubmit) {
      onSearchSubmit(searchTerm);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (onSearchSubmit) {
      onSearchSubmit(searchTerm);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Search..."
        onChange={handleInputChange}
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;
