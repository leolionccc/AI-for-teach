import request from "./request"

// =========================
// 章节管理
// =========================

export function listChaptersApi() {
  return request({
    url: "/exams/chapters",
    method: "get"
  })
}

export function createChapterApi(data) {
  return request({
    url: "/exams/chapters",
    method: "post",
    data
  })
}

export function updateChapterApi(id, data) {
  return request({
    url: `/exams/chapters/${id}`,
    method: "put",
    data
  })
}

export function deleteChapterApi(id) {
  return request({
    url: `/exams/chapters/${id}`,
    method: "delete"
  })
}

// =========================
// 考核配置
// =========================

export function listExamConfigsApi(params) {
  return request({
    url: "/exams/configs",
    method: "get",
    params
  })
}

export function createExamConfigApi(data) {
  return request({
    url: "/exams/configs",
    method: "post",
    data
  })
}

export function updateExamConfigApi(id, data) {
  return request({
    url: `/exams/configs/${id}`,
    method: "put",
    data
  })
}

export function deleteExamConfigApi(id) {
  return request({
    url: `/exams/configs/${id}`,
    method: "delete"
  })
}