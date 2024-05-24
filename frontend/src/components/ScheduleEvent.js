import React, { useState } from 'react';
import axios from 'axios';

const ScheduleEvent = () => {
  const [formData, setFormData] = useState({
    venName: '',
    eventName: 'SIMPLE',
    eventType: 'level',
    startTime: '',
    duration: '',
  });
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    console.log('Scheduling Event with Data:', formData);  // Debugging print
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/event', formData);
      console.log('Response:', response.data);  // Debugging print
      setResult({ status: 'success', message: `Event scheduled successfully for VEN ${formData.venName}.` });
    } catch (error) {
      console.error('Error:', error);  // Debugging print
      if (error.response && error.response.data.message) {
        setResult({ status: 'error', message: error.response.data.message });
      } else {
        setResult({ status: 'error', message: 'An error occurred while scheduling the event.' });
      }
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
          <label htmlFor="eventName">Event Name</label>
          <select
            id="eventName"
            name="eventName"
            className="form-control"
            value={formData.eventName}
            onChange={handleChange}
          >
            <option value="SIMPLE">Simple</option>
            <option value="ELECTRICITY_PRICE">Electricity Price</option>
            <option value="LOAD_DISPATCH">Load Dispatch</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="eventType">Event Type</label>
          <select
            id="eventType"
            name="eventType"
            className="form-control"
            value={formData.eventType}
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
