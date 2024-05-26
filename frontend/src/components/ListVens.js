import React, { useState } from 'react';
import axios from 'axios';

const ListVens = ({ vens, fetchAllVens }) => {
  const [result, setResult] = useState(null);

  const handleRemove = async (venName) => {
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
    <div className="container mt-4 table-container">
      <h1 className="text-center">View and Remove VENs</h1>
      <div className="result mt-3">
        {result && (
          <div className={`alert ${result.status === 'success' ? 'alert-success' : 'alert-danger'}`}>
            {result.message}
          </div>
        )}
      </div>
      {vens.length > 0 ? (
        <table className="table mt-4 table-centered">
          <thead>
            <tr>
              <th>VEN Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {vens.map(ven => (
              <tr key={ven.ven_name}>
                <td>{ven.ven_name}</td>
                <td>
                  <button className="btn btn-danger" onClick={() => handleRemove(ven.ven_name)}>
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No VENs found.</p>
      )}
    </div>
  );
};

export default ListVens;
