import React, {useState} from 'react';
import { useSearchParams } from 'next/navigation';

import { Job } from '@/utils/api';
import { SideNavBar } from '@/components/sideNavBar';

export default function Results() {
    const searchParams = useSearchParams();
    const dataString = searchParams.get('data');
    const names_ids: string[][] = dataString ? JSON.parse(dataString) : [];

    const jobs: Job[] = names_ids.map(([siteName, jobId]) => ({
        jobId,
        siteName,
        status: 'processing',
        progress: 0,
      }));

      

    return (
        <div>
            <SideNavBar jobs={jobs}></SideNavBar>
        </div>
    )
}