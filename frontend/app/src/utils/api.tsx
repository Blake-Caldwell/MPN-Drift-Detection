import axios from 'axios'

const api = axios.create(
    {
        baseURL: 'http://localhost:8000'
    }
)

const uploadFiles = async (files: File[]): Promise<any> => {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }
    try {
      const response = await api.post('/upload_files', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Files failed to upload');
    }
  };

  const apiModule = { api, uploadFiles };
  export default apiModule;