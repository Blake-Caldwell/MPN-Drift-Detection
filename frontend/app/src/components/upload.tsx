"use client";
import { useState, useRef, ChangeEvent, DragEvent } from "react";
import apiModule from "../utils/api";
import ErrorPopup from "./error";

import { Button } from "./ui/button";
import { Separator } from "./ui/separator";
import { ScrollArea } from "./ui/scroll-area";

import { useRouter } from "next/navigation";

import { YamlConfigDialog } from "./yamlConfigCreate";

export const FileUpload = () => {
  const [fileEnter, setFileEnter] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [showFileList, setShowFileList] = useState(false);

  const [showError, setShowError] = useState<string[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const router = useRouter();

  const [showYamlConfigDialog, setShowYamlConfigDialog] = useState(false); 

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setFileEnter(true);
  };

  const handleDragLeave = () => {
    setFileEnter(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    // wont let duplicate files
    e.preventDefault();
    setFileEnter(false);

    if (e.dataTransfer.files) {
      const newFiles = Array.from(e.dataTransfer.files);
      const tempFiles: File[] = Array.from(newFiles).filter((file) => {
        const fileName = file.name;
        const extension = fileName.split(".").pop();
        if (extension !== "csv" && extension !== "yaml") {
          setShowError([`Unsupported file format!`]); // Give Errors message when wrong file types are placed
          return false;
        }
        if (
          selectedFiles.some((selectedFile) => selectedFile.name === fileName)
        ) {
          setShowError([`File has already been uploaded!`]); // Error message when the same file is uploaded
          return false;
        }
        return true;
      });

      setSelectedFiles((prevFiles) => [...prevFiles, ...tempFiles]);
      setShowFileList(true);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    // for file browser
    if (e.target.files) {
      const newFiles = e.target.files;
      const tempFiles: File[] = Array.from(newFiles).filter((file) => {
        const fileName = file.name;
        const extension = fileName.split(".").pop();
        if (extension !== "csv" && extension !== "yaml") {
          setShowError([`Unsupported file format!`]);
          return false;
        }
        if (
          selectedFiles.some((selectedFile) => selectedFile.name === fileName)
        ) {
          setShowError([`File has already been uploaded!`]);
          return false;
        }
        return true;
      });
      setSelectedFiles((prevFiles) => [...prevFiles, ...tempFiles]);
      setShowFileList(true);

      if (fileInputRef.current) {
        //used to clear saved state from file browser
        fileInputRef.current.value = "";
      }
    }
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prevFiles) => {
      const updatedFiles = prevFiles.filter((_, i) => i !== index);
      setShowFileList(updatedFiles.length > 0);
      return updatedFiles;
    });
  };

  const handleYamlConfigCreate = (file: File) => { // adds the yaml into the list (used by the yamlConfig component)
    setSelectedFiles((prevFiles) => [...prevFiles, file]);
    setShowYamlConfigDialog(false);
  };

  const handleSubmitClick = async () => {

    const hasYamlFile = selectedFiles.some((file) =>
      file.name.endsWith(".yaml")
    );

    if (!hasYamlFile) {
      setShowYamlConfigDialog(true);
      return;
    }

    setIsLoading(true); // shows loading spinner

    let site_map = new Map<string, File[]>();
    let configFile: File | null = null;

    selectedFiles.forEach((value: File) => {
      if (value.name.endsWith(".yaml") || value.name.endsWith(".yml")) {
        configFile = value;
      } else {
        const nameParts = value.name.split("_");
        if (nameParts.length >= 2) {
          const site_name = nameParts[1];
          if (site_map.has(site_name)) {
            site_map.get(site_name)?.push(value);
          } else {
            site_map.set(site_name, [value]);
          }
        } else {
          console.warn(`Skipping file ${value.name} due to unexpected format`);
        }
      }
    });

    try {
      const uploadPromises = Array.from(site_map.entries()).map(
        ([site_name, dataFiles]) => {
          const files = [...dataFiles];

          if (configFile) {
            files.push(configFile);
          }

          return apiModule
            .uploadFiles(site_name, files)
            .then((result) => result);
        }
      );

      const results = await Promise.all(uploadPromises);

      const queryParam = encodeURIComponent(JSON.stringify(results));
      router.push(`/results?ids=${queryParam}`);
    } catch (error: unknown) {
      if (error instanceof Error) {
        console.error(error);
        setShowError([error.name, error.message]);
      }
    }

    setIsLoading(false); // remove spinner
    setSelectedFiles([]); // empty after upload
  };

  return (
    <div>
      <div
        className="box-container mx-auto bg-slate-50 p-6 rounded-lg shadow-2xl transition duration-300 ease-in-out hover:scaletransform-105"
        style={{ width: "420px" }}
      >
        <div
          className={`border-2 border-dashed ${
            fileEnter ? "border-blue-500" : "border-slate-300"
          } p-4 rounded-lg flex flex-col items-center justify-center h-48`}
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
      {/* <button onClick={() => logFiles()}>
        Log Collected Files
      </button>  USE THIS FOR DEBUGGING*/}
      {showFileList && (
  <div
    className={`text-white pt-8 transition-opacity duration-700 ${
      showFileList == true ?  "opacity-100" : "opacity-0"
      }`}
  >
    <h2 className="text-center text-lg pb-3">
      {selectedFiles.length} Selected File(s)
    </h2>
    <ScrollArea className="h-48 w-full rounded-lg border bg-slate-50">
      <div className="p-4">
        {selectedFiles.map((file, index) => (
          <div key={index}>
            <div className="flex items-center text-sm font-semibold justify-between text-slate-900">
              <span>{file.name}</span>
              <button
                className="focus:outline-none hover:scale-105"
                onClick={() => handleRemoveFile(index)}
              >
                <svg
                  fill="#972121"
                  width="48px"
                  height="24px"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                  stroke="#972121"
                >
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g
                    id="SVGRepo_tracerCarrier"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  ></g>
                  <g id="SVGRepo_iconCarrier">
                    <path d="M13.5,11.7928932 L16.1464466,9.14644661 C16.3417088,8.95118446 16.6582912,8.95118446 16.8535534,9.14644661 C17.0488155,9.34170876 17.0488155,9.65829124 16.8535534,9.85355339 L14.2071068,12.5 L16.8535534,15.1464466 C17.0488155,15.3417088 17.0488155,15.6582912 16.8535534,15.8535534 C16.6582912,16.0488155 16.3417088,16.0488155 16.1464466,15.8535534 L13.5,13.2071068 L10.8535534,15.8535534 C10.6582912,16.0488155 10.3417088,16.0488155 10.1464466,15.8535534 C9.95118446,15.6582912 9.95118446,15.3417088 10.1464466,15.1464466 L12.7928932,12.5 L10.1464466,9.85355339 C9.95118446,9.65829124 9.95118446,9.34170876 10.1464466,9.14644661 C10.3417088,8.95118446 10.6582912,8.95118446 10.8535534,9.14644661 L13.5,11.7928932 L13.5,11.7928932 Z M7.28441797,17.4602766 C7.56940871,17.8022655 7.99158013,18 8.43674989,18 L19.5,18 C20.3284271,18 21,17.3284271 21,16.5 L21,8.5 C21,7.67157288 20.3284271,7 19.5,7 L8.43674989,7 C7.99158013,7 7.56940871,7.19773451 7.28441797,7.5397234 L3.15085414,12.5 L7.28441797,17.4602766 Z M2.11588936,12.1799078 L6.51619669,6.899539 C6.99118126,6.32955752 7.69480029,6 8.43674989,6 L19.5,6 C20.8807119,6 22,7.11928813 22,8.5 L22,16.5 C22,17.8807119 20.8807119,19 19.5,19 L8.43674989,19 C7.69480029,19 6.99118126,18.6704425 6.51619669,18.100461 L2.11588936,12.8200922 C1.96137021,12.6346692 1.96137021,12.3653308 2.11588936,12.1799078 Z"></path>
                  </g>
                </svg>
              </button>
            </div>
            {index !== selectedFiles.length - 1 && (
              <Separator className="my-2" />
            )}
          </div>
        ))}
      </div>
    </ScrollArea>

    <div className="flex justify-center mt-4">
      <Button onClick={handleSubmitClick}>Submit</Button>
    </div>
  </div>
)}

      {isLoading && ( //https://flowbite.com/docs/components/spinner/
        <div
          role="status"
          className="flex flex-col items-center justify-center mt-12"
        >
          <svg
            aria-hidden="true"
            className="inline w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-gray-600 dark:fill-gray-100"
            viewBox="0 0 100 101"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
              fill="currentColor"
            />
            <path
              d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
              fill="currentFill"
            />
          </svg>
          <span className="sr-only">Loading...</span>
        </div>
      )}

      {showError && (
        <ErrorPopup items={showError} onClose={() => setShowError(null)} />
      )}

      <YamlConfigDialog
        open={showYamlConfigDialog}
        onOpenChange={setShowYamlConfigDialog}
        onConfigCreate={handleYamlConfigCreate}
      />
    </div>
  );
};
