// ViewResult.tsx
import React, { useState, useEffect } from "react";
import apiModule from "@/utils/api";
import { LineChart } from "@/components/charts/line";
import { BarChart } from "@/components/charts/bar";
import {
  transformLineData,
  transformBarData,
  LineData,
} from "@/utils/chartUtils";

import { Label } from "./ui/label";
import { ScrollArea } from "./ui/scroll-area";
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
          console.log(data);

          const activityDataArray = Object.entries(data).map(
            ([activity, activityData]: [string, any]) => {
              const parsedActivityData = JSON.parse(activityData.data);
              const lineData = transformLineData(
                parsedActivityData,
                activityData.drift
              );
              const barData = transformBarData(parsedActivityData);

              console.log(activityData.drift);
              return {
                activity,
                target_column: activityData.target_column,
                lineData,
                barData,
                driftData: activityData.drift,
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
    <div className="text-slate-50">
      <h2 className="text-3xl font-serif font-medium ml-4 mb-1">
        {result.siteName}
      </h2>
      <Separator className="h-0.5"></Separator>
      {result.activityDataArray.map(
        ({ activity, target_column, lineData, barData, driftData }: any) => (
          <div key={activity} className="bg-brightness-90 pt-6 mb-10">
            <h3 className="ml-24 text-lg">
              {(activity as string).charAt(0).toUpperCase() +
                (activity as string).slice(1)}
            </h3>
            <Separator className="ml-20 mb-5 w-56"></Separator>
            <div
              className="w-11/12 bg-slate-100 text-slate-900 rounded-lg pb-3 pl-5"
              style={{ height: "400px" }}
            >
              {lineData ? (
                <LineChart
                  data={lineData}
                  target={target_column}
                  driftData={driftData}
                />
              ) : (
                <div>Loading Lines...</div>
              )}
            </div>
            <div className="mt-5 flex w-11/12">
              <div
                className="w-10/12 bg-slate-100 text-slate-900 rounded-lg pb-3 pl-3 mr-3"
                style={{ height: "400px" }}
              >
                {barData ? (
                  <BarChart
                    data={barData}
                    target={target_column + " ROLLING SUM"}
                  />
                ) : (
                  <div>Writing Bars...</div>
                )}
              </div>
              <div className=" w-2/12 bg-slate-100 text-slate-900 rounded-lg">
                <ScrollArea className="h-96 rounded-md border">
                  <div className="p-4">
                    <Label className="justify-center text-md mb-2">
                      Identified Drift Occurences
                    </Label>
                    <Separator className="fill-slate-950 bg-slate-950 mb-3 h-0.5"></Separator>
                    {driftData &&
                      Object.entries(driftData).map(
                        ([date, drift]: [string, any]) => (
                          <React.Fragment key={date}>
                            <div className="border-solid border-slate-700 border-2 mt-1 mb-1 p-1 border-opacity-10 rounded-md shadow-md">
                              <div className="text-sm">
                                <strong>Date:</strong> {date.split("T")[0]}
                              </div>
                              <div className="text-sm">
                                <strong>Status:</strong> {drift.status}
                              </div>
                              <div className="text-sm">
                                <strong>Difference:</strong> {drift.difference}
                              </div>
                              <div className="text-sm">
                                <strong>Z-Score:</strong> {drift.z_score}
                              </div>
                            </div>
                          </React.Fragment>
                        )
                      )}
                  </div>
                </ScrollArea>
              </div>
            </div>
          </div>
        )
      )}
    </div>
  );
}

export default ViewResult;
