import request from "./request"

export function listChatSessionsApi() {
  return request({
    url: "/chat-history/sessions",
    method: "get"
  })
}

export function createChatSessionApi(data) {
  return request({
    url: "/chat-history/sessions",
    method: "post",
    data
  })
}

export function updateChatSessionApi(id, data) {
  return request({
    url: `/chat-history/sessions/${id}`,
    method: "put",
    data
  })
}

export function deleteChatSessionApi(id) {
  return request({
    url: `/chat-history/sessions/${id}`,
    method: "delete"
  })
}

export function listChatMessagesApi(sessionId) {
  return request({
    url: `/chat-history/sessions/${sessionId}/messages`,
    method: "get"
  })
}

export function createChatMessageApi(sessionId, data) {
  return request({
    url: `/chat-history/sessions/${sessionId}/messages`,
    method: "post",
    data
  })
}