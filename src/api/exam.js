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

// =========================
// 考试流程
// =========================

export function startExamApi(data) {
  return request({
    url: "/exams/start",
    method: "post",
    data
  })
}

export function listExamRecordsApi() {
  return request({
    url: "/exams/records",
    method: "get"
  })
}

export function listExamQuestionsApi(examId) {
  return request({
    url: `/exams/${examId}/questions`,
    method: "get"
  })
}

export function submitExamAnswerApi(examId, data) {
  return request({
    url: `/exams/${examId}/answer`,
    method: "post",
    data
  })
}

export function submitExamApi(examId) {
  return request({
    url: `/exams/${examId}/submit`,
    method: "post"
  })
}

export function getExamReportApi(examId) {
  return request({
    url: `/exams/${examId}/report`,
    method: "get"
  })
}