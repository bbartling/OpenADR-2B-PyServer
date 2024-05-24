import React, { useState } from 'react';
import axios from 'axios';

const RegisterVen = () => {
  const [venName, setVenName] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    console.log('Registering VEN:', venName);  // Debugging print
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/ven', { venName });
      console.log('Response:', response.data);  // Debugging print
      setResult({ status: 'success', message: `VEN ${venName} registered successfully.` });
    } catch (error) {
      console.error('Error:', error);  // Debugging print
      if (error.response && error.response.data.message === "VEN already registered") {
        setResult({ status: 'error', message: `VEN ${venName} is already registered.` });
      } else {
        setResult({ status: 'error', message: 'An error occurred while registering the VEN.' });
      }
    }
  };

  return (
    <div className="container mt-4">
      <h1 className="text-center">Register VEN</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="venName">VEN Name</label>
          <input
            type="text"
            id="venName"
            name="venName"
            className="form-control"
            value={venName}
            onChange={(e) => setVenName(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary mt-3">Register VEN</button>
      </form>
      <div className="result mt-3">
        {result && (
          <div className={`alert ${result.status === 'success' ? 'alert-success' : 'alert-danger'}`}>
            {result.message}
          </div>
        )}
      </div>
    </div>
  );
};

export default RegisterVen;
