import axios from 'axios'

const http = axios.create({
  baseURL: '/api', // 代理到后端
  timeout: 10000,
})

// 可根据需要添加请求/响应拦截器
http.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error),
)

export default http
