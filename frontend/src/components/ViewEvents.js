import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ViewEvents = () => {
  const [events, setEvents] = useState([]);
  const [result, setResult] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [currentEvent, setCurrentEvent] = useState(null);

  const fetchAllEvents = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8080/api/all_events');
      setEvents(response.data);
    } catch (error) {
      console.error('Error fetching events:', error);
      setResult({ status: 'error', message: 'Failed to fetch events.' });
    }
  };

  const handleCancel = async () => {
    if (!currentEvent) return;
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/cancel_event', currentEvent);
      setResult({ status: response.data.status, message: response.data.message });

      setShowModal(false); // Close the modal
      fetchAllEvents();  // Refresh the event list
    } catch (error) {
      console.error('Error canceling event:', error);
      setResult({ status: 'error', message: 'Failed to cancel event. Please try again.' });
    }
  };

  const handleShowModal = (ven_id, event_id) => {
    setCurrentEvent({ ven_id, event_id });
    setShowModal(true);
  };

  useEffect(() => {
    fetchAllEvents();
    const interval = setInterval(fetchAllEvents, 5000); // Polling interval of 5 seconds
    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, []);

  return (
    <div className="container mt-4">
      <h1 className="text-center">View and Cancel Events</h1>
      <div className="result mt-3">
        {result && (
          <div className={`alert ${result.status === 'success' ? 'alert-success' : 'alert-danger'}`}>
            {result.message}
          </div>
        )}
      </div>
      {events.length > 0 ? (
        <table className="table mt-4">
          <thead>
            <tr>
              <th>VEN ID</th>
              <th>Event ID</th>
              <th>Event Name</th>
              <th>Event Type</th>
              <th>Start Time</th>
              <th>Duration (minutes)</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {events.map(event => (
              <tr key={event.event_id}>
                <td>{event.ven_id}</td>
                <td>{event.event_id}</td>
                <td>{event.event_name}</td>
                <td>{event.event_type}</td>
                <td>{new Date(event.event_start).toLocaleString()}</td>
                <td>{event.event_duration}</td>
                <td>
                  <button className="btn btn-danger" onClick={() => handleShowModal(event.ven_id, event.event_id)}>
                    Cancel
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No events found.</p>
      )}

      {showModal && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={() => setShowModal(false)}>&times;</span>
            <h2>Cancel Event</h2>
            <p>Are you sure you want to cancel this event? Note - all VENs need to check in with the VTN and receive the event cancellation before it will be removed from the VTN.</p>
            <button className="btn btn-secondary" onClick={() => setShowModal(false)}>Close</button>
            <button className="btn btn-danger" onClick={handleCancel}>Cancel Event</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ViewEvents;
