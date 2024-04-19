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

  const response = await api.post('/upload_files', formData, { //leave the try/catch to outside
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

const apiModule = { api, uploadFiles };
export default apiModule;