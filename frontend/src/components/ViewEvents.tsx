import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Event {
  ven_id: string;
  ven_name: string;
  event_id: string;
  signal_name: string;
  signal_type: string;
  event_start: string;
  event_duration: number;
}

const ViewEvents: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [result, setResult] = useState<{ status: string, message: string } | null>(null);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [currentEvent, setCurrentEvent] = useState<{ ven_id: string; event_id: string } | null>(null);

  const fetchAllEvents = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8080/api/all_events');
      setEvents(response.data);
    } catch (error) {
      console.error('Error fetching events:', error);
      setResult({ status: 'error', message: 'Failed to fetch events.' });
    }
  };

  useEffect(() => {
    fetchAllEvents();
    const interval = setInterval(fetchAllEvents, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (result) {
      const timer = setTimeout(() => setResult(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [result]);

  const handleCancel = async () => {
    if (!currentEvent) return;
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/cancel_event', currentEvent);
      setResult({ status: response.data.status, message: response.data.message });
      setShowModal(false);
      fetchAllEvents();
    } catch (error) {
      console.error('Error canceling event:', error);
      setResult({ status: 'error', message: 'Failed to cancel event. Please try again.' });
    }
  };

  const handleShowModal = (ven_id: string, event_id: string) => {
    setCurrentEvent({ ven_id, event_id });
    setShowModal(true);
  };

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
        <table className="table mt-4 table-centered">
          <thead>
            <tr>
              <th>VEN Name</th>
              <th>Event ID</th>
              <th>Signal Name</th>
              <th>Signal Type</th>
              <th>Start Time</th>
              <th>Duration (minutes)</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {events.map(event => (
              <tr key={event.event_id}>
                <td>{event.ven_name}</td>
                <td>{event.event_id}</td>
                <td>{event.signal_name}</td>
                <td>{event.signal_type}</td>
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
            <p>Are you sure you want to cancel this event?</p>
            <p>Note that all VENs need to check in with the server and receive the updated event notification before the event will be removed from the server.</p>
            <button className="btn btn-secondary" onClick={() => setShowModal(false)}>No, Go Back!</button>
            <button className="btn btn-danger" onClick={handleCancel}>Yes, Cancel Event!</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ViewEvents;
