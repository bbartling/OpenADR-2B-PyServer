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

interface Ven {
  ven_id: string;
  ven_name: string;
}

const ScheduleEvent: React.FC = () => {
  const [formData, setFormData] = useState<EventFormData>({
    venName: '',
    signalName: 'SIMPLE',
    signalType: 'level',
    startTime: '',
    duration: '120',
  });
  const [vens, setVens] = useState<Ven[]>([]);
  const [selectedVens, setSelectedVens] = useState<string[]>([]);
  const [result, setResult] = useState<{ status: string, message: string } | null>(null);

  // Fetch VENs
  const fetchAllVens = async () => {
    try {
      console.log('Fetching all VENs...');
      const response = await axios.get('http://127.0.0.1:8080/api/list_vens');
      console.log('VENs fetched:', response.data);
      setVens(response.data);
    } catch (error) {
      console.error('Error fetching VENs:', error);
    }
  };

  useEffect(() => {
    fetchAllVens();
  }, []);

  useEffect(() => {
    if (result) {
      const timer = setTimeout(() => setResult(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [result]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    console.log(`Form data change: ${e.target.name} = ${e.target.value}`);
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleVenSelection = (ven_id: string) => {
    setSelectedVens(prev => 
      prev.includes(ven_id) ? prev.filter(id => id !== ven_id) : [...prev, ven_id]
    );
    console.log('Selected VENs:', selectedVens);
  };

  const handleSelectAll = () => {
    if (selectedVens.length === vens.length) {
      setSelectedVens([]);
    } else {
      setSelectedVens(vens.map(ven => ven.ven_id));
    }
    console.log('Selected All VENs:', selectedVens);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    console.log('Submitting event with data:', formData);
    console.log('Selected VENs for the event:', selectedVens);

    try {
      for (const ven_id of selectedVens) {
        const payload = {
          ...formData,
          ven_ids: selectedVens
        };
        console.log('Payload:', payload);
        const response = await axios.post('http://127.0.0.1:8080/api/event', payload);
        console.log('Response for VEN ID:', ven_id, response.data);
      }
      setResult({ status: 'success', message: `Event scheduled successfully for selected VENs.` });
    } catch (error) {
      console.error('Error scheduling event:', error);
      setResult({ status: 'error', message: 'An error occurred while scheduling the event.' });
    }
  };

  return (
    <div className="container mt-4">
      <h1 className="text-center">Schedule OpenADR Event</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="label-select-vens">Select VENs</label>
          <div className="ven-list">
            <div className="ven-item">
              <input
                type="checkbox"
                id="selectAll"
                onChange={handleSelectAll}
                checked={selectedVens.length === vens.length}
              />
              <label htmlFor="selectAll">Select All</label>
            </div>
            {vens.map(ven => (
              <div key={ven.ven_id} className="ven-item">
                <label htmlFor={ven.ven_id}>{ven.ven_name}</label>
                <input
                  type="checkbox"
                  id={ven.ven_id}
                  value={ven.ven_id}
                  onChange={() => handleVenSelection(ven.ven_id)}
                  checked={selectedVens.includes(ven.ven_id)}
                />
              </div>
            ))}
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="signalName" className="label-event-details">Event Name</label>
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
            <label htmlFor="signalType" className="label-event-details">Event Type</label>
            <select
              id="signalType"
              name="signalType"
              className="form-control"
              value={formData.signalType}
              onChange={handleChange}
            >
              <option value="level">Level</option>
            </select>
            <label htmlFor="level" className="label-event-details">Level</label>
            <select
              id="level"
              name="level"
              className="form-control"
              value={formData.level !== undefined ? formData.level : ''}
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
            <label htmlFor="signalType" className="label-event-details">Event Type</label>
            <select
              id="signalType"
              name="signalType"
              className="form-control"
              value={formData.signalType}
              onChange={handleChange}
            >
              <option value="price">Price</option>
            </select>
            <label htmlFor="price" className="label-event-details">Price ($/kWh)</label>
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
            <label htmlFor="signalType" className="label-event-details">Event Type</label>
            <select
              id="signalType"
              name="signalType"
              className="form-control"
              value={formData.signalType}
              onChange={handleChange}
            >
              <option value="level">Level</option>
            </select>
            <label htmlFor="setpoint" className="label-event-details">kW Setpoint</label>
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
          <label htmlFor="startTime" className="label-event-details">Start Time (UTC)</label>
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
          <label htmlFor="duration" className="label-event-details">Duration (minutes)</label>
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
