"use client"
import { useState, useRef, ChangeEvent, DragEvent } from "react";

export const FileUpload = () => {
  const [fileEnter, setFileEnter] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setFileEnter(true);
  };

  const handleDragLeave = () => {
    setFileEnter(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setFileEnter(false);

    if (e.dataTransfer.files) {
      [...e.dataTransfer.files].forEach((file, i) => {
        console.log(`File ${i + 1}: ${file.name}`);
      });
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      [...e.target.files].forEach((file, i) => {
        console.log(`File ${i + 1}: ${file.name}`);
      });
    }
  };

  return (
    <div className="box-container mx-auto bg-slate-50 p-6 rounded-lg shadow-lg"> 
      <div
        className={`border-2 border-dashed ${
          fileEnter ? "border-blue-500" : "border-slate-300"
        } p-4 rounded-lg flex flex-col items-center justify-center h-48 cursor-pointer transition duration-300 ease-in-out`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <svg
          className={`w-8 h-8 mb-2 ${
            fileEnter ? "text-blue-500" : "text-slate-400"
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          ></path>
        </svg>
        <p
          className={`text-center ${
            fileEnter ? "text-blue-500" : "text-slate-400"
          }`}
        >
          {fileEnter
            ? "Release to drop the files here"
            : "Drag and drop files here or click to upload"}
        </p>
      </div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        style={{ display: "none" }}
      />
    </div>
  );
};