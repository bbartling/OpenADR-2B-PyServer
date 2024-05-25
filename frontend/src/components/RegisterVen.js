import React, { useState } from 'react';
import axios from 'axios';

const RegisterVen = ({ fetchAllVens }) => {
  const [venName, setVenName] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Submitting VEN name:', venName);  // Log the submitted VEN name
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/ven', { venName });
      console.log('Server response:', response.data);  // Log the server response
      setResult({ status: response.data.status, message: response.data.message });
      if (fetchAllVens) {
        fetchAllVens();  // Refresh the VEN list if fetchAllVens is available
      }
    } catch (error) {
      console.error('Error registering VEN:', error);
      if (error.response && error.response.data) {
        // Server responded with a status other than 2xx
        console.error('Server error response:', error.response.data);
        setResult({ status: 'error', message: error.response.data.message || 'Failed to register VEN. Please try again.' });
      } else {
        // Network or other error
        setResult({ status: 'error', message: 'Failed to register VEN. Please try again.' });
      }
    }
  };

  return (
    <div className="container mt-4">
      <h1 className="text-center">Register VEN</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input 
            type="text" 
            className="form-control" 
            value={venName} 
            onChange={(e) => setVenName(e.target.value)} 
            placeholder="Enter VEN name" 
          />
        </div>
        <button type="submit" className="btn btn-primary">Register VEN</button>
      </form>
      {result && (
        <div className={`alert mt-3 ${result.status === 'success' ? 'alert-success' : 'alert-danger'}`}>
          {result.message}
        </div>
      )}
    </div>
  );
};

export default RegisterVen;
