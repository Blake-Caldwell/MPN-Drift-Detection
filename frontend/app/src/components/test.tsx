
import React, { useState, useEffect } from 'react';
import api from '../app/api'

interface Data {
  message: string;
}

function Test_Fast() {
  const [data, setData] = useState<Data | null>(null);

  
    const fetchData = async () => {
      try {
        const response = await api.get<Data>('http://localhost:8000/test'); // Update with your FastAPI URL
        setData(response.data);
      } catch (error) {
        console.error("Error fetching data:", error); 
      }
    };

    fetchData();
 

  return (
    <div>
      {data 
        ? <h1>{data.message}</h1> 
        : <p>Loading data...</p>
      }
    </div>
  );
}

export default Test_Fast;