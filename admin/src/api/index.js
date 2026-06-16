import axios from 'axios';
import { ElMessage } from 'element-plus';

const baseURL = import.meta.env.VITE_API_BASE;
const http = axios.create({ baseURL, timeout: 30000 });

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken');
  if (token) config.data = { ...config.data, adminToken: token };
  return config;
});

http.interceptors.response.use(
  (resp) => {
    const data = resp.data;
    if (data && data.code !== 0) {
      ElMessage.error(data.message || '请求失败');
      return Promise.reject(data);
    }
    return data && data.data !== undefined ? data.data : data;
  },
  (err) => {
    ElMessage.error(err.message || '网络异常');
    return Promise.reject(err);
  }
);

export const api = {
  login: (username, password) => http.post('/adminLogin', { username, password }),
  listIndustries: () => http.post('/listIndustries', {}),
  saveIndustry: (payload) => http.post('/saveIndustry', payload),
  listPromptTemplates: (payload = {}) => http.post('/listPromptTemplates', payload),
  savePromptTemplate: (payload) => http.post('/savePromptTemplate', payload),
};
