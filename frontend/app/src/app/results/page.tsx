"use client";
import React, { useEffect, useState } from "react";
import { LineChart } from "@/components/charts/line";
import { BarChart } from "@/components/charts/bar";
import {
  LineData,
  transformLineData,
  BarData,
  transformBarData,
} from "@/utils/chartUtils";

export default function Results() {
  const [line_data, setLineData] = useState<null | LineData>(null);
  const [bar_data, setBarData] = useState<null | BarData>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/testing_charts/trucking.json");
        const jsonData = await response.json();
        const transformedLineData = transformLineData(jsonData);
        const transformedBarData = transformBarData(jsonData);
        //console.log(transformedBarData.length)
        setLineData(transformedLineData);
        setBarData(transformedBarData);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

  return (
    <div className=" text-white">
      <div className="pt-10 ">
        <div className="flex justify-center">
          <h1 className="text-6xl font-serif mb-8">
            [Activity] for [Mine]
          </h1>
        </div>
        <div className="ml-20">
          <div
            className=" w-10/12 bg-slate-50 text-slate-900 rounded-lg pb-12"
            style={{ height: "400px" }}
          >
            {line_data ? (
              <LineChart data={line_data} />
            ) : (
              <div>Loading Lines...</div>
            )}
          </div>
          <div
            className=" mt-10 w-2/3 bg-slate-50 text-slate-900 rounded-lg pb-12"
            style={{ height: "400px" }}
          >
            {bar_data ? (
              <BarChart data={bar_data} />
            ) : (
              <div>Writing Bars...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
