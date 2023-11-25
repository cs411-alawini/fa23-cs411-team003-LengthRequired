// App.js
import React from 'react';
import SearchBar from './SearchBar';
import './App.css';
import Login from './Login';
import SignUp from './Signup';

function App() {
  const handleSearchSubmit = (searchTerm) => {
    console.log('Search submitted:', searchTerm);
    // You can add more logic here to handle the search term
  };

  return (
    <div className="App">
      <header className="App-header">
        <SignUp />
        <Login />
        {/* <SearchBar onSearchSubmit={handleSearchSubmit} /> */}
      </header>
    </div>
  );
}

export default App;
