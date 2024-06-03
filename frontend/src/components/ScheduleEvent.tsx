import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface EventFormData {
  venName: string;
  signalName: string;
  signalType: string;
  startTime: string;
  duration: string;
  level?: number;
  price?: number;
  setpoint?: number;
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
        {formData.signalName === 'SIMPLE' && (
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
            </select>
            <label htmlFor="level">Level</label>
            <select
              id="level"
              name="level"
              className="form-control"
              value={formData.level || ''}
              onChange={(e) => setFormData({ ...formData, level: Number(e.target.value) })}
              required
            >
              <option value="">Select Level</option>
              <option value="0">0</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
            </select>
          </div>
        )}
        {formData.signalName === 'ELECTRICITY_PRICE' && (
          <div className="form-group">
            <label htmlFor="signalType">Event Type</label>
            <select
              id="signalType"
              name="signalType"
              className="form-control"
              value={formData.signalType}
              onChange={handleChange}
            >
              <option value="price">Price</option>
            </select>
            <label htmlFor="price">Price ($/kWh)</label>
            <input
              type="number"
              id="price"
              name="price"
              className="form-control"
              value={formData.price || ''}
              onChange={(e) => setFormData({ ...formData, price: Number(e.target.value) })}
              step="0.01"
              required
            />
          </div>
        )}
        {formData.signalName === 'LOAD_DISPATCH' && (
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
            </select>
            <label htmlFor="setpoint">kW Setpoint</label>
            <input
              type="number"
              id="setpoint"
              name="setpoint"
              className="form-control"
              value={formData.setpoint || ''}
              onChange={(e) => setFormData({ ...formData, setpoint: Number(e.target.value) })}
              step="0.1"
              required
            />
          </div>
        )}
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
