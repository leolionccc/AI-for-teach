import axios from "axios"
import { ElMessage } from "element-plus"

const request = axios.create({
  baseURL: "/api/v1",
  timeout: 100000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem("access_token")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    let message = "请求失败，请稍后重试"

    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail

      if (typeof detail === "string") {
        message = detail
      } else if (status === 401) {
        message = "登录状态已失效，请重新登录"
        localStorage.removeItem("access_token")
        localStorage.removeItem("user_info")
        window.location.href = "/login"
      } else if (status === 403) {
        message = "没有权限访问"
      } else if (status === 404) {
        message = "接口不存在"
      } else if (status === 500) {
        message = "服务器内部错误"
      }
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request