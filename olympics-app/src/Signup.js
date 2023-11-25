import React, { useState } from 'react';
import axios from 'axios';

function Signup() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleEmailChange = (event) => {
    setEmail(event.target.value);
  };

  const handleUsernameChange = (event) => {
    setUsername(event.target.value);
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const handleConfirmPasswordChange = (event) => {
    setConfirmPassword(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!email.trim() || !username.trim()) {
        alert('Please enter both email and username.');
        return;
    }

    if (password !== confirmPassword) {
      alert("Passwords don't match.");
      return;
    }

    try {
      // Replace with the actual URL of your sign-up API
      const response = await axios.post('http://olympicsgw/api/registration', {
        email,
        username,
        password
      });
      console.log('Server Response:', response.data);
      // Additional logic based on response (e.g., redirecting the user)
    } catch (error) {
      console.error('Sign Up Error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>
          Email:
          <input type="email" value={email} onChange={handleEmailChange} />
        </label>
      </div>
      <div>
        <label>
          Username:
          <input type="text" value={username} onChange={handleUsernameChange} />
        </label>
      </div>
      <div>
        <label>
          Password:
          <input type="password" value={password} onChange={handlePasswordChange} />
        </label>
      </div>
      <div>
        <label>
          Confirm Password:
          <input type="password" value={confirmPassword} onChange={handleConfirmPasswordChange} />
        </label>
      </div>
      <div>
        <button type="submit">Sign Up</button>
      </div>
    </form>
  );
}

export default Signup;
