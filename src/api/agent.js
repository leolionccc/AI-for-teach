import request from "./request"

export function listAgentsApi() {
  return request({
    url: "/agents",
    method: "get"
  })
}

export function getAgentDetailApi(id) {
  return request({
    url: `/agents/${id}`,
    method: "get"
  })
}

export function createAgentApi(data) {
  return request({
    url: "/agents",
    method: "post",
    data
  })
}

export function updateAgentApi(id, data) {
  return request({
    url: `/agents/${id}`,
    method: "put",
    data
  })
}

export function deleteAgentApi(id) {
  return request({
    url: `/agents/${id}`,
    method: "delete"
  })
}