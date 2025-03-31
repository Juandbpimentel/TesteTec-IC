// src/apiService.js
import axios from 'axios'

const apiUrl = import.meta.env.VITE_API_URL || 'https://testetec-ic.rj.r.appspot.com/'

export const apiService = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const testApiService = () => {
  return apiService.get('/').then((response) => response.data)
}
