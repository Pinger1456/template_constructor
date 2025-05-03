import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// При необходимости, добавить interceptors для обработки ошибок/авторизации

export default api;
