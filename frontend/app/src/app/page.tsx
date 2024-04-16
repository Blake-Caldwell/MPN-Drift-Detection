import React, { useState, useEffect } from 'react'
import Test_Fast from '@/components/test';
import { FileUpload } from '@/components/upload';
 

export default function Home() {
  return (

    <div className='bg-gradient-to-br from-slate-500 to-slate-800 text-white min-h-screen flex justify-center'>
      <div className="flex flex-col items-center pt-40">
        <h1 className="text-6xl font-serif  mb-8">
          Idoba Drift Detector
        </h1>
        <FileUpload></FileUpload>
        <div className='pt-20'> 
          <Test_Fast></Test_Fast>
        </div>

      </div>
    </div>


  );
}
