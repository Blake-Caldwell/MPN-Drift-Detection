"use client"
import React, {useEffect, useState} from "react";
import { LineChart } from "@/components/charts/line";
import { LineData, transformLineData } from "@/utils/chartUtils";

export default function Results() {

    const [data, setData] = useState<null | LineData>(null);

    useEffect(() => { 
      const fetchData = async () => {
        try {
          const response = await fetch("/testing_charts/bogging.json");
          const jsonData = await response.json();
          const transformedData = transformLineData(jsonData);
          setData(transformedData);
        } catch (error) {
          console.error("Error fetching data:", error);
        }
      };

      })


  return (
    <div className="flex justify-center items-center text-white">
      <div className="pt-10 flex-col">
        <h1 className="text-6xl font-serif mb-8">Results for [Mine Name]</h1>
        <div className="flex items-center justify-center">
        <div className="h-2/5">
            {data ? <LineChart data={data} /> : <div>Loading...</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
