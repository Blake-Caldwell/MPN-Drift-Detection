import axios from 'axios'

const api = axios.create(
  {
    baseURL: 'http://localhost:8000'
  }
)

const uploadFiles = async (site_name: string, files: File[]): Promise<any> => {
  const formData = new FormData();

  formData.append('site_name', site_name);
  for (const file of files) {
    formData.append('files', file);
  }

  try {
    const response = await api.post('/upload_files', formData, {
      params: {
        site_name: site_name,
      },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading files:', error);
    throw error;
  }
};

export interface Job {
  jobId: string;
  siteName: string;
  status: string;
  progress: number;
}

export interface Poll {
  status: string;
  progress: number;
}

const pollJob = async (jobid: string): Promise<Poll> => {

  try
  {
    const response = await api.get(`/progress/${jobid}`);
    const { status, progress } = response.data;
    return {
      status,
      progress,
    }

  } catch(error) {
    console.error(`Error polling job ${jobid}:`, error);
    throw error;
  }

}


const fetchResult = async (jobid: string): Promise<any> => {

  try
  {
    const response = await api.get(`/progress/${jobid}`);
    const { result } = response.data;
    return {
      result
    }

  } catch(error) {
    console.error(`Error polling job ${jobid}:`, error);
    throw error;
  }

}


const apiModule = {
  api,
  uploadFiles,
  pollJob,
  fetchResult
};

export default apiModule;