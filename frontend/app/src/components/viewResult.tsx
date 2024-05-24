// ViewResult.tsx
import React, { useState, useEffect } from "react";
import apiModule from "@/utils/api";
import { LineChart } from "@/components/charts/line";
import { BarChart } from "@/components/charts/bar";
import { transformLineData, transformBarData, LineData } from "@/utils/chartUtils";
import { Separator } from "./ui/separator";

function ViewResult({ selectedJobId }: { selectedJobId: string | null }) {
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const fetchResult = async () => {
      if (selectedJobId) {
        try {
          const name = await apiModule.fetchJobDetails(selectedJobId, ["site_name"]);
          const data = await apiModule.fetchResults(selectedJobId);
          console.log(data);
  
          const activityDataArray = Object.entries(data).map(
            ([activity, activityData]: [string, any]) => {
              const parsedActivityData = JSON.parse(activityData.data);
              const target_column = activityData.target_column;
              const lineData = transformLineData(parsedActivityData);
              const barData = transformBarData(parsedActivityData);
              return {
                activity,
                target_column,
                lineData,
                barData,
                driftData: parsedActivityData.drift,
              };
            }
          );
  
          setResult({ siteName: name.site_name, activityDataArray });
        } catch (error) {
          console.error("Error occurred while fetching job details.", error);
          setResult(null);
        }
      }
    };
  
    fetchResult();
  }, [selectedJobId]);

  if (!selectedJobId || !result) {
    return null;
  }

  return (
    <div className=" text-slate-50">
      <h2 className="text-3xl font-serif font-medium ml-4 mb-1">{result.siteName}</h2>
      <Separator className=" h-0.5"></Separator>

      {result.activityDataArray.map(({ activity, target_column, lineData, barData }: any) => (
        
        <div key={activity} className=" bg-brightness-90 pt-6">
          <h3 className="ml-24 text-lg ">{(activity as string).charAt(0).toUpperCase() + (activity as string).slice(1)}</h3>
          <Separator className="ml-20 mb-5 w-56"></Separator>
          <div
            className="w-11/12 bg-slate-100 text-slate-900 rounded-lg pb-12"
            style={{ height: "400px" }}
          >
            {lineData ? (
              <LineChart data={lineData} target={target_column} />
            ) : (
              <div>Loading Lines...</div>
            )}
          </div>
          <div
            className="mt-10 w-11/12 bg-slate-100 text-slate-900 rounded-lg pb-12"
            style={{ height: "400px" }}
          >
            {barData ? <BarChart data={barData} target={target_column + " ROLLING SUM"} /> : <div>Writing Bars...</div>}
          </div>
        </div>
      ))}
    </div>
  );
}

export default ViewResult;