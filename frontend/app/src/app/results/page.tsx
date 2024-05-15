"use client";
import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import apiModule, { Job } from "@/utils/api";

// https://ui.shadcn.com/docs/components/
// following components are from this free component lib

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";

import ErrorPopup from "@/components/error";
import ViewResult from "@/components/viewResult"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Results() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ResultsContent />
    </Suspense>
  );
}

function ResultsContent() {
  const [isAsideVisible, setIsAsideVisible] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

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
                  transform="matrix(-1, 0, 0, 1, 0, 0)"
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
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button disabled={job.status !== "Complete"} variant="ghost" className=" text-s h-8 underline">
                    Download
                  </Button>
                  <Button disabled={job.status !== "Complete"} variant="secondary" className="h-8"
                      onClick={() => {setSelectedJobId(job.jobId); console.log(job.jobId)}}>
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
              className="h-8 w-15 p-1 mt-3 rounded-full bg-transparent hover:bg-opacity-20"
            >
              <svg
                fill="#dae4ec"
                width="32px"
                height="32px"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                stroke="#dae4ec"
                strokeWidth="0.6"
              >
                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                <g
                  id="SVGRepo_tracerCarrier"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                ></g>
                <g id="SVGRepo_iconCarrier">
                  {" "}
                  <path d="M20.2928932,13 L16.5,13 C16.2238576,13 16,12.7761424 16,12.5 C16,12.2238576 16.2238576,12 16.5,12 L20.2928932,12 L19.1464466,10.8535534 C18.9511845,10.6582912 18.9511845,10.3417088 19.1464466,10.1464466 C19.3417088,9.95118446 19.6582912,9.95118446 19.8535534,10.1464466 L21.8535534,12.1464466 C22.0488155,12.3417088 22.0488155,12.6582912 21.8535534,12.8535534 L19.8535534,14.8535534 C19.6582912,15.0488155 19.3417088,15.0488155 19.1464466,14.8535534 C18.9511845,14.6582912 18.9511845,14.3417088 19.1464466,14.1464466 L20.2928932,13 L20.2928932,13 Z M2.5,7 C2.22385763,7 2,6.77614237 2,6.5 C2,6.22385763 2.22385763,6 2.5,6 L10.5,6 C10.7761424,6 11,6.22385763 11,6.5 C11,6.77614237 10.7761424,7 10.5,7 L2.5,7 Z M2.5,11 C2.22385763,11 2,10.7761424 2,10.5 C2,10.2238576 2.22385763,10 2.5,10 L7.5,10 C7.77614237,10 8,10.2238576 8,10.5 C8,10.7761424 7.77614237,11 7.5,11 L2.5,11 Z M2.5,15 C2.22385763,15 2,14.7761424 2,14.5 C2,14.2238576 2.22385763,14 2.5,14 L10.5,14 C10.7761424,14 11,14.2238576 11,14.5 C11,14.7761424 10.7761424,15 10.5,15 L2.5,15 Z M2.5,19 C2.22385763,19 2,18.7761424 2,18.5 C2,18.2238576 2.22385763,18 2.5,18 L7.5,18 C7.77614237,18 8,18.2238576 8,18.5 C8,18.7761424 7.77614237,19 7.5,19 L2.5,19 Z M13,3.5 C13,3.22385763 13.2238576,3 13.5,3 C13.7761424,3 14,3.22385763 14,3.5 L14,20.5 C14,20.7761424 13.7761424,21 13.5,21 C13.2238576,21 13,20.7761424 13,20.5 L13,3.5 Z"></path>{" "}
                </g>
              </svg>
            </Button>
          )}
        </div>
        <div>
          {selectedJobId ? (
            <Suspense fallback={<div>Loading result...</div>}>
              <ViewResult selectedJobId={selectedJobId} />
            </Suspense>
            //<Test_Results></Test_Results>
          ) : (
            <div> </div>
          )}
        </div>
      </main>
    </div>
  );
}
