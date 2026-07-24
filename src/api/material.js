import request from "./request"

export function listMaterialsApi() {
  return request({
    url: "/materials",
    method: "get"
  })
}

export function getMaterialDetailApi(id) {
  return request({
    url: `/materials/${id}`,
    method: "get"
  })
}

export function uploadMaterialApi(formData) {
  return request({
    url: "/materials",
    method: "post",
    data: formData
  })
}

export function deleteMaterialApi(id) {
  return request({
    url: `/materials/${id}`,
    method: "delete"
  })
}