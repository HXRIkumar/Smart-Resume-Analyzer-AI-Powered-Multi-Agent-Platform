import { api } from './client.js'

export const login = async (email, password) => {
  const formData = new FormData()
  formData.append('username', email)
  formData.append('password', password)
  const response = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
  return response.data
}

export const register = async (data) => {
  const response = await api.post('/auth/register', data)
  return response.data
}

export const getMe = async () => {
  const response = await api.get('/auth/me')
  return response.data
}

export const googleLogin = async (code) => {
  const response = await api.post('/auth/google-login', { code })
  return response.data
}
