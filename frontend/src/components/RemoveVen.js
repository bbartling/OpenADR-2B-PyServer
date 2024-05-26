import React, { useState } from 'react';
import axios from 'axios';

const RemoveVen = ({ fetchAllVens }) => {
  const [venName, setVenName] = useState('');
  const [result, setResult] = useState(null);

  const handleRemove = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/remove_ven', { venName });
      setResult({ status: response.data.status, message: response.data.message });
      fetchAllVens(); // Refresh the VEN list
    } catch (error) {
      console.error('Error removing VEN:', error);
      setResult({ status: 'error', message: 'Failed to remove VEN. Please try again.' });
    }
  };

  return (
    <div className="container mt-4">
      <h1 className="text-center">Remove VEN</h1>
      <div className="form-group mt-3">
        <input 
          type="text" 
          className="form-control" 
          value={venName} 
          onChange={(e) => setVenName(e.target.value)} 
          placeholder="Enter VEN name" 
        />
      </div>
      <button className="btn btn-danger" onClick={handleRemove}>Remove VEN</button>
      {result && (
        <div className={`alert mt-3 ${result.status === 'success' ? 'alert-success' : 'alert-danger'}`}>
          {result.message}
        </div>
      )}
    </div>
  );
};

export default RemoveVen;
