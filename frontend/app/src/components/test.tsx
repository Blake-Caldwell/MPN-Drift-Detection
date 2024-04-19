'use client';
import React, { useState, useEffect } from 'react';
import apiModule from '../utils/api'



function Test_Fast() {
  const [data, setData] = useState<string | null>(null);

    useEffect(() => { 
    const fetchData = async () => {
      try {
        const response = await apiModule.api.get<string>('http://localhost:8000/test');
        console.log(response.data);
        setData(response.data);
      } catch (error) {
        console.error("Error fetching data:", error); 
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      {data 
        ? <h1>{data}</h1> 
        : <h1>Loading data...</h1>
      }
    </div>
  );

  // return (
  //   <div>
  //     <pre>{JSON.stringify(data, null, 2)}</pre> 
  //   </div>
  // );
}

export default Test_Fast;