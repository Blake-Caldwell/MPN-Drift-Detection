"use client"
import { useState, useRef, ChangeEvent, DragEvent } from "react";

export const FileUpload = () => {
  const [fileEnter, setFileEnter] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setFileEnter(true);
  };

  const handleDragLeave = () => {
    setFileEnter(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => { // wont let duplicate files
    e.preventDefault();
    setFileEnter(false);

    if (e.dataTransfer.files) {
      [...e.dataTransfer.files].forEach((file, i) => { // to be removed, good for testing
        console.log(`File ${i + 1}: ${file.name}`);
      });

      const newFiles = e.dataTransfer.files;
      const tempFiles: File[] = Array.from(newFiles).filter( // this syntax is wild
        (file) => !selectedFiles.some((selectedFile) => selectedFile.name === file.name)
      );
      setSelectedFiles((prevFiles) => [...prevFiles, ...tempFiles]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => { // for file browser
    if (e.target.files) {
      [...e.target.files].forEach((file, i) => {
        console.log(`File ${i + 1}: ${file.name}`);
      });

      const newFiles = e.target.files;
      const tempFiles: File[] = Array.from(newFiles).filter( // this syntax is wild
        (file) => !selectedFiles.some((selectedFile) => selectedFile.name === file.name)
      );
      setSelectedFiles((prevFiles) => [...prevFiles, ...tempFiles]);
    }
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  }

  return (
    <div>
      <div className="box-container mx-auto bg-slate-50 p-6 rounded-lg shadow-2xl transition duration-300 ease-in-out hover:scaletransform-105">
        <div
          className={`border-2 border-dashed ${fileEnter ? "border-blue-500" : "border-slate-300"
            } p-4 rounded-lg flex flex-col items-center justify-center h-48`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <svg
            className={`w-8 h-8 mb-2 ${fileEnter ? "text-blue-500" : "text-slate-400"
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
            className={`text-center ${fileEnter ? "text-blue-500" : "text-slate-400"
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

      {selectedFiles.length > 0 && (

        <div className="text-white pt-8">
          <h2 className="text-center text-xl pb-3"> {selectedFiles.length} Selected Files</h2>
          <ul className="bg-slate-100 rounded-lg">

            {selectedFiles.map((file, index) => (
              <li key={index} className=" flex items-center justify-between text-black px-4 py-2">
                <span>{file.name}</span>
                <button
                  className="text-red-500 hover:text-red-700 focus:outline-none "
                  onClick={() => handleRemoveFile(index)}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    viewBox="0 30 30"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10.185,1.417c-4.741,0-8.583,3.842-8.583,8.583c0,4.74,3.842,8.582,8.583,8.582S18.768,14.74,18.768,10C18.768,5.259,14.926,1.417,10.185,1.417 M10.185,17.68c-4.235,0-7.679-3.445-7.679-7.68c0-4.235,3.444-7.679,7.679-7.679S17.864,5.765,17.864,10C17.864,14.234,14.42,17.68,10.185,17.68 M10.824,10l2.842-2.844c0.178-0.176,0.178-0.46,0-0.637c-0.177-0.178-0.461-0.178-0.637,0l-2.844,2.841L7.341,6.52c-0.176-0.178-0.46-0.178-0.637,0c-0.178,0.176-0.178,0.461,0,0.637L9.546,10l-2.841,2.844c-0.178,0.176-0.178,0.461,0,0.637c0.178,0.178,0.459,0.178,0.637,0l2.844-2.841l2.844,2.841c0.178,0.178,0.459,0.178,0.637,0c0.178-0.176,0.178-0.461,0-0.637L10.824,10z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </li>
            ))}
          </ul>

          <div className="flex justify-center mt-4">
            <button className="bg-green-300 hover:bg-green-400 rounded-3xl text-lg font-semibold text-slate-900 px-6 py-1 transition-all duration-300 ease-in-out transform hover:scale-110">
              Submit
            </button>
          </div>
        </div>
      )}
    </div>



  );
};