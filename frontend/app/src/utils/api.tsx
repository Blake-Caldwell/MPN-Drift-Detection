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
  activities: string[];
}

export interface Poll {
  status: string;
}

//refactor so im not duplicating logic, pass fields wanted in
const fetchJobDetails = async (jobId: string, fields: string[] = []): Promise<any> => {
  try {
    const response = await api.get(`/job/${jobId}`, {
      params: {
        fields: fields.join(','),
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching job details for ${jobId}:`, error);
    throw error;
  }
};

const fetchResults = async(jobId: string): Promise<any> => { // Needed because need to alter data before 

  try {
    const results = await api.get(`/job/${jobId}/results`);
    return results.data;
  } catch (error) {
    console.error(`Error fetching results for ${jobId}:`, error);
    throw error;
  }
};


const apiModule = {
  api,
  uploadFiles,
  fetchJobDetails,
  fetchResults,
};

export default apiModule;