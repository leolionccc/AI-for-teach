import request from "./request"

export function listSystemLogsApi(params) {
  return request({
    url: "/system-logs",
    method: "get",
    params
  })
}

export function getSystemLogDetailApi(id) {
  return request({
    url: `/system-logs/${id}`,
    method: "get"
  })
}