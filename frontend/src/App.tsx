//App.tsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import RegisterVen from './components/RegisterVen';
import ScheduleEvent from './components/ScheduleEvent';
import ViewEvents from './components/ViewEvents';
import ListVens from './components/ListVens';
import './App.css';

interface Ven {
  ven_name: string;
}

const App: React.FC = () => {
  const [vens, setVens] = useState<Ven[]>([]);

  const fetchAllVens = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8080/api/list_vens');
      setVens(response.data);
    } catch (error) {
      console.error('Error fetching VENs:', error);
    }
  };

  useEffect(() => {
    fetchAllVens();
  }, []);

  return (
    <div className="App">
      <div className="main-content">
        <RegisterVen fetchAllVens={fetchAllVens} />
        <ScheduleEvent />
        <ViewEvents />
        <ListVens vens={vens} fetchAllVens={fetchAllVens} />
      </div>
    </div>
  );
}

export default App;
