import React, { useState } from 'react';


const Dropdown = ({ options, onOptionSelected }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);

  const toggleDropdown = () => setShowDropdown(!showDropdown);

  const handleSelect = (option) => {
    setSelectedOption(option);
    setShowDropdown(false);
    onOptionSelected(option);
  };

  return (
    <div className="dropdown">
      <button className="dropbtn" onClick={toggleDropdown}>
        {selectedOption || 'Select an option'}
      </button>
      {showDropdown && (
        <div className="dropdown-content">
          {options.map((option, index) => (
            <a key={index} href="#" onClick={() => handleSelect(option)}>
              {option}
            </a>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dropdown;
