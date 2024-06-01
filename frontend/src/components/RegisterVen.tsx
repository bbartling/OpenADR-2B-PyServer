import React, { useState } from 'react';
import axios from 'axios';

interface RegisterVenProps {
  fetchAllVens: () => void;
}

const RegisterVen: React.FC<RegisterVenProps> = ({ fetchAllVens }) => {
  const [venName, setVenName] = useState<string>('');
  const [result, setResult] = useState<{ status: string, message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/ven', { venName });
      setResult({ status: response.data.status, message: response.data.message });
      fetchAllVens();
    } catch (error) {
      console.error('Error registering VEN:', error);
      setResult({ status: 'error', message: 'Failed to register VEN. Please try again.' });
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
