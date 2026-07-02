import axios from 'axios'

// Dynamically read environment variable to seamlessly switch target entrypoints
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1'

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Hardened Request Interceptor to automatically attach secure tokens
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('JWT_TOKEN')
  const apiKey = localStorage.getItem('API_KEY')
  
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  } else if (apiKey) {
    config.headers['X-API-Key'] = apiKey
  }
  
  return config
}, error => {
  return Promise.reject(error)
})

// Response Interceptor for global error handling and CORS safety verification
apiClient.interceptors.response.use(response => response, error => {
  if (error.response && error.response.status === 401) {
    // Hard-redirect if a 401 Unauthorized occurs
    localStorage.removeItem('JWT_TOKEN')
    localStorage.removeItem('API_KEY')
    window.location.href = '/login'
  }
  return Promise.reject(error)
})

export default apiClient
