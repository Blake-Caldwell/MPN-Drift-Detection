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
            const name = await apiModule.fetchJobDetails(selectedJobId, [
                "site_name",
              ]);

              const data = await apiModule.fetchResults(selectedJobId);

              const activityDataArray = Object.entries(data).map(
                ([activity, activityDataString]: [string, any]) => {
                
                  const activityData = JSON.parse(activityDataString);
                  const lineData = transformLineData(activityData);
                  const barData = transformBarData(activityData);
                  return { activity, lineData, barData, driftData: activityData.drift };
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
    <div>
      <h2 className="text-4xl font-serif font-medium  mb-1">{result.siteName}</h2>
      <Separator className=" h-0.5"></Separator>

      {result.activityDataArray.map(({ activity, lineData, barData }: any) => (
        
        <div key={activity} className=" bg-brightness-90 pt-6">
          <h3 className="ml-24 text-lg ">{(activity as string).charAt(0).toUpperCase() + (activity as string).slice(1)}</h3>
          <Separator className="ml-20 mb-5 w-56"></Separator>
          <div
            className="w-11/12 bg-slate-100 text-slate-900 rounded-lg pb-12"
            style={{ height: "400px" }}
          >
            {lineData ? (
              <LineChart data={lineData} />
            ) : (
              <div>Loading Lines...</div>
            )}
          </div>
          <div
            className="mt-10 w-11/12 bg-slate-100 text-slate-900 rounded-lg pb-12"
            style={{ height: "400px" }}
          >
            {barData ? <BarChart data={barData} /> : <div>Writing Bars...</div>}
          </div>
        </div>
      ))}
    </div>
  );
}

export default ViewResult;