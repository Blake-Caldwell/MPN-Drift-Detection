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

import { DotLoader, BounceLoader, FadeLoader } from "react-spinners";

import ErrorPopup from "@/components/error";
import ViewResult from "@/components/viewResult";

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


  const handleReturnButtonClick = () => {
    window.location.href = '/'; // Navigates to the home page
  };


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
    <div className="flex">
      <aside className="min-w-80 bg-gray-700 p-6  fixed min-h-screen z-40 shadow-gray-700 shadow-xl">
        <ScrollArea>
          <div className="cards-container flex flex-col space-y-4 bg-transparent">
            <div className="flex justify-between">
              <Button variant="default" className="text-xs h-8">
                Download All
              </Button>
              <Label color="#dae4ec" className="opacity-90 mt-2">
                MPN Drift Detector
              </Label>
            </div>

            {jobs.map((job) => {
              if (job.status === "Complete" && selectedJobId === null) {
                setSelectedJobId(job.jobId);
              }
              return (
                <Card key={job.jobId}>
                  <CardHeader>
                    <CardTitle>{job.siteName}</CardTitle>

                    <CardDescription className="text-xs italic">
                      {job.jobId}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-col justify-center items-center">
                    <Label className="opacity-80">Status</Label>
                    <br></br>
                    <Label>{job.status}</Label>
                    <br />
                    <br />
                    <Progress className="h-2" value={job.progress} />
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    <Button
                      disabled={job.status !== "Complete"}
                      variant="ghost"
                      className="text-s h-8 underline mr-10"
                    >
                      Download
                    </Button>

                    <Button
                      disabled={job.status !== "Complete"}
                      variant="secondary"
                      className="h-8"
                      onClick={() => {
                        setSelectedJobId(job.jobId);
                      }}
                    >
                      <span className="mr-2">View</span>
                      {job.status !== "Complete" && <BounceLoader size="8" />}
                    </Button>
                  </CardFooter>
                </Card>
              );
            })}

            </div>
            <br/>
            <div className="flex-col justify-center items-center">
              <Button variant="default" className="text-xs h-8" onClick={handleReturnButtonClick}>
                Return
              </Button>
            </div>

          </ScrollArea>
      </aside>
      <main className=" ml-96 flex-grow mt-0.5 pt-1.5">
        <div>
          {selectedJobId ? (
            <div className="p-10 bg-gray-700 bg-opacity-80 shadow-gray-700 shadow-xl rounded-xl">
              <Suspense fallback={<div>Loading result...</div>}>
                <ViewResult selectedJobId={selectedJobId} />
              </Suspense>
            </div>
          ) : (
            <div className="h-screen">
              <div className="flex justify-center items-center h-full opacity-70">
                <DotLoader color="#f1f5f9" />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
