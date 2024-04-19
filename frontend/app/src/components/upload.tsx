"use client"
import { useState, useRef, ChangeEvent, DragEvent } from "react";
import apiModule from '../utils/api'
import ErrorPopup from './error'

export const FileUpload = () => {
  const [fileEnter, setFileEnter] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showError, setShowError] = useState<string[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);

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

      const newFiles = e.target.files;
      const tempFiles: File[] = Array.from(newFiles).filter( // this syntax is wild
        (file) => !selectedFiles.some((selectedFile) => selectedFile.name === file.name)
      );
      setSelectedFiles((prevFiles) => [...prevFiles, ...tempFiles]);

      if (fileInputRef.current) { //used to clear saved state from file browser
        fileInputRef.current.value = "";
      }
    }
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  }

  const handleSubmitClick = async () => {
    console.log("Submit!")
    setIsLoading(true); //shows loading spinner

    try {
      const result = await apiModule.uploadFiles(selectedFiles);
      console.log(result);
      // page direction should be here towards the dashboard or a loading screen
    } catch (error: unknown) {

      if (error instanceof Error) //https://typescript.tv/errors/#ts18046
      {
        console.error(error);
        setShowError([error.name, error.message]);
        setIsLoading(false);
      }
    }
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
      {/* <button onClick={() => logFiles()}>
        Log Collected Files
      </button>  USE THIS FOR DEBUGGING*/}
      {selectedFiles.length > 0 ? (

        <div className="text-white pt-8 transition-opacity ease-in duration-700 opacity-100">
          <h2 className="text-center text-xl pb-3"> {selectedFiles.length} Selected File(s)</h2>
          <ul className="bg-slate-50 rounded-lg">

            {selectedFiles.map((file, index) => (
              <li key={index} className=" flex items-center justify-between text-slate-900 px-4 py-2">
                <span>{file.name}</span>
                <button
                  className="text-red-500 hover:text-red-700 focus:outline-none hover:scale-105"
                  onClick={() => handleRemoveFile(index)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    stroke="currentColor"
                    strokeWidth="1.1">

                    <path fillRule="evenodd" d="M10.185,1.417c-4.741,0-8.583,3.842-8.583,8.583c0,4.74,3.842,8.582,8.583,8.582S18.768,14.74,18.768,10C18.768,5.259,14.926,1.417,10.185,1.417 M10.185,17.68c-4.235,0-7.679-3.445-7.679-7.68c0-4.235,3.444-7.679,7.679-7.679S17.864,5.765,17.864,10C17.864,14.234,14.42,17.68,10.185,17.68 M10.824,10l2.842-2.844c0.178-0.176,0.178-0.46,0-0.637c-0.177-0.178-0.461-0.178-0.637,0l-2.844,2.841L7.341,6.52c-0.176-0.178-0.46-0.178-0.637,0c-0.178,0.176-0.178,0.461,0,0.637L9.546,10l-2.841,2.844c-0.178,0.176-0.178,0.461,0,0.637c0.178,0.178,0.459,0.178,0.637,0l2.844-2.841l2.844,2.841c0.178,0.178,0.459,0.178,0.637,0c0.178-0.176,0.178-0.461,0-0.637L10.824,10z" clipRule="evenodd" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>

          <div className="flex justify-center mt-4">
            <button className=" bg-green-400 hover:bg-green-500 rounded-3xl text-lg font-semibold text-slate-900 px-6 py-1 transition-all duration-300 ease-in-out transform hover:scale-110"
              onClick={handleSubmitClick}>
              Submit
            </button>
          </div>
        </div>
      ) : (
        <div className="text-white pt-8 transition-opacity ease-in duration-700 opacity-0">
          {/* Empty state content */}
        </div>)}

      {isLoading && ( //https://flowbite.com/docs/components/spinner/
        <div role="status" className="flex flex-col items-center justify-center mt-12">
        <svg aria-hidden="true" className="inline w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-gray-600 dark:fill-gray-100" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
          <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
        </svg>
        <span className="sr-only">Loading...</span>
      </div>
      )}

      {showError && (
        <ErrorPopup
          items={showError}
          onClose={() => setShowError(null)}
        />
      )}
    </div>

  );
};