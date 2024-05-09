import React from 'react'
import { FileUpload } from '@/components/upload';
import Link from 'next/link';
 

export default function Home() {
  return (

    <div className='flex justify-center'>
      <div className="flex flex-col items-center pt-40">
        <h1 className="text-6xl font-serif  mb-8">
          Idoba Drift Detector
        </h1>
        <FileUpload></FileUpload>

        <Link href="/test_results">
          <button className="mt-8 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            Results test
          </button>
        </Link>

      </div>
    </div>


  );
}
