// ListVens.tsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Ven {
  ven_name: string;
  last_report: string | null;
  last_report_units: string | null;
  last_report_time: string | null;
  connection_quality: number;
}

interface ListVensProps {
  vens: Ven[];
  fetchAllVens: () => void;
}

const ENV_MODE = "DEV" // get from Vite or wherever
const urlBase = ENV_MODE === "DEV" ? "http://127.0.0.1:8080" : "prod_stuff"

const ListVens: React.FC<ListVensProps> = ({ vens, fetchAllVens }) => {
  const [result, setResult] = useState<{ status: string, message: string } | null>(null);

  useEffect(() => {
    fetchAllVens();
    const interval = setInterval(fetchAllVens, 5000);
    return () => clearInterval(interval);
  }, [fetchAllVens]);

  useEffect(() => {
    if (result) {
      const timer = setTimeout(() => setResult(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [result]);

  const handleRemove = async (venName: string) => {
    try {
      const response = await axios.post(`${urlBase}/api/remove_ven`, { venName });
      setResult({ status: response.data.status, message: response.data.message });
      fetchAllVens();  // Refresh the list after removing a VEN
    } catch (error) {
      console.error('Error removing VEN:', error);
      setResult({ status: 'error', message: 'Failed to remove VEN. Please try again.' });
    }
  };

  return (
    <div className="container mt-4">
      <h1 className="text-center">View and Remove VENs</h1>
      <div className="result mt-3">
        {result && (
          <div className={`alert ${result.status === 'success' ? 'alert-success' : 'alert-danger'}`}>
            {result.message}
          </div>
        )}
      </div>
      {vens.length > 0 ? (
        <div className="table-container">
          <table className="table mt-4 table-centered">
            <thead>
              <tr>
                <th>VEN Name</th>
                <th>Last Report Value</th>
                <th>Units</th>
                <th>Timestamp</th>
                <th>Connection Quality</th>  {/* Add this line */}
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {vens.map(ven => (
                <tr key={ven.ven_name}>
                  <td>{ven.ven_name}</td>
                  <td>{ven.last_report ? ven.last_report : 'No reports yet'}</td>
                  <td>{ven.last_report_units ? ven.last_report_units : 'N/A'}</td>
                  <td>{ven.last_report_time ? new Date(ven.last_report_time).toLocaleString() : 'N/A'}</td>
                  <td>{ven.connection_quality.toFixed(2)}%</td>  {/* Add this line */}
                  <td>
                    <button className="btn btn-danger" onClick={() => handleRemove(ven.ven_name)}>
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>No VENs found.</p>
      )}
    </div>
  );
};

export default ListVens;
