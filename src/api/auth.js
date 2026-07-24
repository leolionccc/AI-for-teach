import request from "./request"

export function registerApi(data) {
  return request({
    url: "/auth/register",
    method: "post",
    data
  })
}

export function loginApi(data) {
  return request({
    url: "/auth/login",
    method: "post",
    data
  })
}

export function getCurrentUserApi() {
  return request({
    url: "/users/me",
    method: "get"
  })
}

export function updateCurrentUserApi(data) {
  return request({
    url: "/users/me",
    method: "put",
    data
  })
}

export function updatePasswordApi(data) {
  return request({
    url: "/users/me/password",
    method: "put",
    data
  })
}