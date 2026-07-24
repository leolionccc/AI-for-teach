import request from "./request"

export function listModelConfigsApi() {
  return request({
    url: "/model-configs",
    method: "get"
  })
}

export function getActiveModelConfigApi() {
  return request({
    url: "/model-configs/active",
    method: "get"
  })
}

export function createModelConfigApi(data) {
  return request({
    url: "/model-configs",
    method: "post",
    data
  })
}

export function updateModelConfigApi(id, data) {
  return request({
    url: `/model-configs/${id}`,
    method: "put",
    data
  })
}

export function activateModelConfigApi(id) {
  return request({
    url: `/model-configs/${id}/activate`,
    method: "post"
  })
}

export function deleteModelConfigApi(id) {
  return request({
    url: `/model-configs/${id}`,
    method: "delete"
  })
}