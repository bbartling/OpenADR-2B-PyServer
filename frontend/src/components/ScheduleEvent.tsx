import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface EventFormData {
  venName: string;
  signalName: string;
  signalType: string;
  startTime: string;
  duration: string;
}

const ScheduleEvent: React.FC = () => {
  const [formData, setFormData] = useState<EventFormData>({
    venName: '',
    signalName: 'SIMPLE',
    signalType: 'level',
    startTime: '',
    duration: '',
  });
  const [result, setResult] = useState<{ status: string, message: string } | null>(null);

  // Dummy function to simulate fetching events
  const fetchAllEvents = async () => {
    try {
      // Replace the URL with your actual endpoint
      const response = await axios.get('http://127.0.0.1:8080/api/events');
      console.log('Events fetched:', response.data);
    } catch (error) {
      console.error('Error fetching events:', error);
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/event', formData);
      setResult({ status: 'success', message: `Event scheduled successfully for VEN ${formData.venName}.` });
      console.log('Response:', response.data);
    } catch (error) {
      console.error('Error:', error);
      setResult({ status: 'error', message: 'An error occurred while scheduling the event.' });
    }
  };

  return (
    <div className="container mt-4">
      <h1 className="text-center">Schedule OpenADR Event</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="venName">VEN Name</label>
          <input
            type="text"
            id="venName"
            name="venName"
            className="form-control"
            value={formData.venName}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="signalName">Event Name</label>
          <select
            id="signalName"
            name="signalName"
            className="form-control"
            value={formData.signalName}
            onChange={handleChange}
          >
            <option value="SIMPLE">Simple</option>
            <option value="ELECTRICITY_PRICE">Electricity Price</option>
            <option value="LOAD_DISPATCH">Load Dispatch</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="signalType">Event Type</label>
          <select
            id="signalType"
            name="signalType"
            className="form-control"
            value={formData.signalType}
            onChange={handleChange}
          >
            <option value="level">Level</option>
            <option value="price">Price</option>
            <option value="priceRelative">Relative Price</option>
            <option value="priceMultiplier">Price Multiplier</option>
            <option value="setpoint">Setpoint</option>
            <option value="delta">Delta</option>
            <option value="multiplier">Multiplier</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="startTime">Start Time (UTC)</label>
          <input
            type="datetime-local"
            id="startTime"
            name="startTime"
            className="form-control"
            value={formData.startTime}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="duration">Duration (minutes)</label>
          <input
            type="number"
            id="duration"
            name="duration"
            className="form-control"
            value={formData.duration}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary mt-3">Send Event</button>
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

export default ScheduleEvent;
