"use client";
import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import apiModule, { Job } from "@/utils/api";
import { Card } from "@/components/ui/card";

export default function Results() {
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
    <div>
      <aside className="sidebar w-1/5 bg-gray-300 p-4">
        <div className="cards-container flex flex-col space-y-4">
          {jobs.map((job) => (
            <Card key={job.jobId}>
              <h3>{job.siteName}</h3>
              <p className="opacity-50 text-xs italic">{job.jobId}</p>
              <p>Status: {job.status}</p>
              <p>Progress: {job.progress}%</p>
              {job.status === "complete" && (
                <button onClick={() => handleViewResult(job.jobId)}>
                  View Result
                </button>
              )}
            </Card>
          ))}
        </div>
      </aside>
      <main className="content w-4/5">
        <h1>activity charts go here!</h1>
     </main>
    </div>
  );
}
