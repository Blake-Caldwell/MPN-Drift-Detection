'use client'
import React, { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";

import apiModule, { Job, Poll } from "@/utils/api";

interface SideNavBarProps {
  jobs: Job[];
  onViewResult: (uuid: string) => void;
}

export const SideNavBar: React.FC<SideNavBarProps> = ({
  jobs,
  onViewResult,
}) => {
  const [jobsData, setJobsData] = useState<Job[]>(jobs);

  useEffect(() => {
    const fetchJobsData = async () => {
      try {
        const updatedJobsData = await Promise.all(
          jobsData.map(async (job) => {
            const pollData = await apiModule.fetchJobDetails(job.jobId, ["status", "progress"]);
            return {
              ...job,
              status: pollData.status,
              progress: pollData.progress,
            };
          })
        );
        setJobsData(updatedJobsData);
      } catch (error) {
        console.error("Error fetching job data:", error);
      }

      console.log("here!")
    };

    const intervalId = setInterval(fetchJobsData, 5000); // Poll every 5 seconds

    return () => {
        clearInterval(intervalId);
    };
  }, [jobsData]);


  return (
    <div>
        {jobsData.map((job) => (
            <Card key={job.jobId}>
                <h3>Site Name: {job.siteName}</h3>
                <p className="opacity-50">Job ID: {job.jobId}</p>
                <p>Status: {job.status}</p>
                <p>Progress: {job.progress}%</p>
                {job.status === 'complete' && (
                    <button onClick={() => onViewResult(job.jobId)}>View Result</button>
                )}
            </Card>
        ))}
    </div>
  )
};
