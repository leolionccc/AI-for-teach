import request from "./request"

// =========================
// 考试运行
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