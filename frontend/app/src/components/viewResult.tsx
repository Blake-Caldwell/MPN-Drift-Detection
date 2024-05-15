// ViewResult.tsx
import React, { useState, useEffect } from "react";
import apiModule from "@/utils/api";
import { LineChart } from "@/components/charts/line";
import { BarChart } from "@/components/charts/bar";
import { transformLineData, transformBarData } from "@/utils/chartUtils";

function ViewResult({ selectedJobId }: { selectedJobId: string | null }) {
  const [result, setResult] = useState<any>(null);

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

  if (!selectedJobId || !result) {
    return null;
  }

  return (
    <div>
      <h2>{result.siteName}</h2>

      {result.activityDataArray.map(({ activity, lineData, barData }: any) => (
        <div key={activity}>
          <h3>Activity: {activity}</h3>
          <div
            className="w-10/12 bg-slate-50 text-slate-900 rounded-lg pb-12"
            style={{ height: "400px" }}
          >
            {lineData ? (
              <LineChart data={lineData} />
            ) : (
              <div>Loading Lines...</div>
            )}
          </div>
          <div
            className="mt-10 w-2/3 bg-slate-50 text-slate-900 rounded-lg pb-12"
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