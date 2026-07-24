import request from "./request"

export function buildMaterialIndexApi(data) {
  return request({
    url: "/rag/materials/build-index",
    method: "post",
    data
  })
}

export function buildAllMaterialIndexesApi() {
  return request({
    url: "/rag/materials/build-all",
    method: "post"
  })
}

export function ragSearchApi(data) {
  return request({
    url: "/rag/search",
    method: "post",
    data
  })
}