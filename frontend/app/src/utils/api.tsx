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

const apiModule = { api, uploadFiles };
export default apiModule;