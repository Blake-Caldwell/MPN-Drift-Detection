import React from 'react'
import { FileUpload } from '@/components/upload';
import Link from 'next/link';

import { Separator } from '@/components/ui/separator';
 

export default function Home() {
  return (

    <div className='flex justify-center'>
      <div className="flex flex-col items-center pt-20">
        <h1 className="text-5xl font-serif  mb-2">
          Idoba Drift Detector
        </h1>
        <Separator className=' mb-5 w-96 h-0.5 bg-gray-200'></Separator>
        <FileUpload></FileUpload>

        {/* <Link href="/test_results">
          <button className="mt-8 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            Results test
          </button>
        </Link> */}

      </div>
    </div>


  );
}
