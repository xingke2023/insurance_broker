import axios from 'axios';
import { API_URL } from '../config';

const API_BASE_URL = API_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const policyAPI = {
  // 获取所有保单
  getAllPolicies: () => api.get('/policies/'),

  // 获取单个保单
  getPolicy: (id) => api.get(`/policies/${id}/`),

  // 创建保单
  createPolicy: (data) => api.post('/policies/', data),

  // 更新保单
  updatePolicy: (id, data) => api.put(`/policies/${id}/`, data),

  // 删除保单
  deletePolicy: (id) => api.delete(`/policies/${id}/`),

  // 获取有效保单
  getActivePolicies: () => api.get('/policies/active_policies/'),

  // 取消保单
  cancelPolicy: (id) => api.post(`/policies/${id}/cancel_policy/`),
};

export default api;
