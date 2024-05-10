"use client";
import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import apiModule, { Job } from "@/utils/api";

// https://ui.shadcn.com/docs/components/
// following components are from this free component ib

import { Button } from "@/components/ui/button";
import { Label } from "@radix-ui/react-label";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Results() {
  const [isAsideVisible, setIsAsideVisible] = useState(true);

  const searchParams = useSearchParams();
  const dataString = searchParams.get("ids");
  let ids: string[] = [];
  if (dataString) {
    try {
      ids = JSON.parse(dataString);
    } catch (error) {
      console.error("Invalid data format:", error);
    }
  }

  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const jobsPromises: Promise<Job>[] = ids.map(async (id) => {
          const { site_name, status, progress } =
            await apiModule.fetchJobDetails(id, [
              "site_name",
              "status",
              "progress",
            ]);
          return {
            jobId: id,
            siteName: site_name,
            status: status,
            progress: progress,
          };
        });

        const fetchedJobs: Job[] = await Promise.all(jobsPromises);
        setJobs(fetchedJobs);
      } catch (error) {
        console.error("Error fetching job details:", error);
      }
    };

    fetchJobs();
    const intervalId = setInterval(fetchJobs, 5000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  const handleViewResult = (jobId: string) => {
    // spin up a fukn chart or two
  };

  return (
    <div className="grid grid-cols-5">
      <aside
        className={`top-0 left-0 w-80 bg-gray-700 p-4 text-white fixed h-full z-40 ease-in-out duration-300 ${
          isAsideVisible ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <ScrollArea>
          <div className="cards-container flex flex-col space-y-4 bg-transparent">
            <div className="flex justify-between">
              <Button variant="default" className=" text-xs h-8">
                {" "}
                Download All
              </Button>
              <Button
                variant="ghost"
                className="h-8 w-15 p-1 rounded-full bg-transparent hover:bg-opacity-20"
                onClick={() => setIsAsideVisible(false)}
              >
                <svg
                  fill="#dae4ec"
                  width="32px"
                  height="32px"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                  stroke="#dae4ec"
                  stroke-width="0.6"
                >
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g
                    id="SVGRepo_tracerCarrier"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  ></g>
                  <g id="SVGRepo_iconCarrier">
                    {" "}
                    <path d="M8.70710678,12 L19.5,12 C19.7761424,12 20,12.2238576 20,12.5 C20,12.7761424 19.7761424,13 19.5,13 L8.70710678,13 L11.8535534,16.1464466 C12.0488155,16.3417088 12.0488155,16.6582912 11.8535534,16.8535534 C11.6582912,17.0488155 11.3417088,17.0488155 11.1464466,16.8535534 L7.14644661,12.8535534 C6.95118446,12.6582912 6.95118446,12.3417088 7.14644661,12.1464466 L11.1464466,8.14644661 C11.3417088,7.95118446 11.6582912,7.95118446 11.8535534,8.14644661 C12.0488155,8.34170876 12.0488155,8.65829124 11.8535534,8.85355339 L8.70710678,12 L8.70710678,12 Z M4,5.5 C4,5.22385763 4.22385763,5 4.5,5 C4.77614237,5 5,5.22385763 5,5.5 L5,19.5 C5,19.7761424 4.77614237,20 4.5,20 C4.22385763,20 4,19.7761424 4,19.5 L4,5.5 Z"></path>{" "}
                  </g>
                </svg>
              </Button>
            </div>

            {jobs.map((job) => (
              <Card key={job.jobId}>
                <CardHeader>
                  <CardTitle>{job.siteName}</CardTitle>

                  <CardDescription className=" text-xs italic">
                    {job.jobId}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-col justify-center items-center">
                  <Label className="opacity-80">Status:</Label>
                  <Label> {job.status}</Label>
                  <br></br> {/* should have like */}
                  <br></br>
                  <Progress value={job.progress} />
                  {job.status === "complete" && (
                    <button onClick={() => handleViewResult(job.jobId)}>
                      View Result
                    </button>
                  )}
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button variant="ghost" className=" text-s h-8 underline">
                    Download
                  </Button>
                  <Button variant="secondary" className="h-8">
                    View
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </aside>
      <main
        className={`content col-span-4 transition-all duration-300 ease-in-out ${
          isAsideVisible ? "ml-4" : "col-start-1 col-end-6"
        }`}
      >
        <div className="flex justify-between items-center mb-4">
          {!isAsideVisible && (
            <Button
              variant="ghost"
              onClick={() => setIsAsideVisible(true)}
              className="h-8 w-15 p-1 mt-3 rounded-full bg-transparent hover:bg-opacity-30"
            >
              <svg
                fill="#dae4ec"
                width="32px"
                height="32px"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                stroke="#dae4ec"
                stroke-width="0.6"
              >
                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                <g
                  id="SVGRepo_tracerCarrier"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                ></g>
                <g id="SVGRepo_iconCarrier">
                  {" "}
                  <path d="M20.2928932,13 L16.5,13 C16.2238576,13 16,12.7761424 16,12.5 C16,12.2238576 16.2238576,12 16.5,12 L20.2928932,12 L19.1464466,10.8535534 C18.9511845,10.6582912 18.9511845,10.3417088 19.1464466,10.1464466 C19.3417088,9.95118446 19.6582912,9.95118446 19.8535534,10.1464466 L21.8535534,12.1464466 C22.0488155,12.3417088 22.0488155,12.6582912 21.8535534,12.8535534 L19.8535534,14.8535534 C19.6582912,15.0488155 19.3417088,15.0488155 19.1464466,14.8535534 C18.9511845,14.6582912 18.9511845,14.3417088 19.1464466,14.1464466 L20.2928932,13 L20.2928932,13 Z M2.5,7 C2.22385763,7 2,6.77614237 2,6.5 C2,6.22385763 2.22385763,6 2.5,6 L10.5,6 C10.7761424,6 11,6.22385763 11,6.5 C11,6.77614237 10.7761424,7 10.5,7 L2.5,7 Z M2.5,11 C2.22385763,11 2,10.7761424 2,10.5 C2,10.2238576 2.22385763,10 2.5,10 L7.5,10 C7.77614237,10 8,10.2238576 8,10.5 C8,10.7761424 7.77614237,11 7.5,11 L2.5,11 Z M2.5,15 C2.22385763,15 2,14.7761424 2,14.5 C2,14.2238576 2.22385763,14 2.5,14 L10.5,14 C10.7761424,14 11,14.2238576 11,14.5 C11,14.7761424 10.7761424,15 10.5,15 L2.5,15 Z M2.5,19 C2.22385763,19 2,18.7761424 2,18.5 C2,18.2238576 2.22385763,18 2.5,18 L7.5,18 C7.77614237,18 8,18.2238576 8,18.5 C8,18.7761424 7.77614237,19 7.5,19 L2.5,19 Z M13,3.5 C13,3.22385763 13.2238576,3 13.5,3 C13.7761424,3 14,3.22385763 14,3.5 L14,20.5 C14,20.7761424 13.7761424,21 13.5,21 C13.2238576,21 13,20.7761424 13,20.5 L13,3.5 Z"></path>{" "}
                </g>
              </svg>
            </Button>
          )}
        </div>
        {/* <h1>activity charts go here! </h1> */}
      </main>
    </div>
  );
}
