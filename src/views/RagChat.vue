<template>
  <div class="chat-page">
    <div class="chat-shell">
      <div class="chat-main-panel">
        <div class="chat-header">
          <div>
            <h1 class="page-title">课程智能体问答</h1>
            <div class="page-subtitle">
              基于课程知识库进行 RAG 问答，支持流式输出和相关资料推荐。
            </div>
          </div>

          <el-button @click="clearChat">
            清空对话
          </el-button>
        </div>

        <div ref="messageContainerRef" class="chat-message-list">
          <div
            v-for="item in messages"
            :key="item.id"
            class="chat-message-row"
            :class="item.role"
          >
            <div class="chat-avatar">
              {{ item.role === "user" ? "我" : "AI" }}
            </div>

            <div class="chat-bubble">
              <div class="chat-role">
                {{ item.role === "user" ? "你" : "课程智能体" }}
              </div>

              <div v-if="item.role === 'user'" class="chat-content plain-text">
                {{ item.content }}
              </div>

              <div
                v-else
                class="chat-content markdown-body"
                v-html="renderMarkdown(item.content)"
              ></div>
            </div>
          </div>

          <div v-if="streaming" class="typing-indicator">
            {{ statusText || "AI 正在思考并检索课程资料..." }}
          </div>
        </div>

        <div class="chat-input-area">
          <el-input
            v-model="question"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="请输入课程问题，例如：什么是人工智能？"
            @keydown.ctrl.enter="handleSend"
          />

          <div class="chat-input-actions">
            <div class="chat-tip">
              Ctrl + Enter 发送。请先在“知识库构建”页面构建索引。
            </div>

            <el-button
              type="primary"
              :loading="streaming"
              @click="handleSend"
            >
              {{ streaming ? "生成中..." : "发送" }}
            </el-button>
          </div>
        </div>
      </div>

      <div class="chat-side-panel">
        <div class="side-title">问答参数</div>

        <el-form label-position="top">
          <el-form-item label="检索片段数">
            <el-input-number
              v-model="topK"
              :min="1"
              :max="20"
              style="width: 100%;"
            />
          </el-form-item>

          <el-form-item label="会话ID">
            <el-input
              v-model="sessionIdText"
              placeholder="自动生成，可为空"
              clearable
            />
          </el-form-item>

          <el-form-item label="智能体ID">
            <el-input
              v-model="agentIdText"
              placeholder="默认自动选择启用智能体"
              clearable
            />
          </el-form-item>
        </el-form>

        <el-divider />

        <div class="side-title">推荐资料</div>

        <div v-if="references.length === 0" class="empty-reference">
          暂无推荐资料
        </div>

        <div
          v-for="item in references"
          :key="item.material_id"
          class="reference-card"
        >
          <div class="reference-name">
            {{ item.material_name }}
          </div>

          <div class="reference-id">
            material_id: {{ item.material_id }}
          </div>
        </div>

        <el-divider />

        <div class="side-title">当前状态</div>

        <div class="status-line">
          当前会话：{{ currentSessionId || "未创建" }}
        </div>

        <div class="status-line">
          流式状态：{{ streaming ? "输出中" : "空闲" }}
        </div>

        <div class="status-line">
          当前任务：{{ statusText || "无" }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref } from "vue"
import { ElMessage } from "element-plus"
import MarkdownIt from "markdown-it"

const question = ref("")
const topK = ref(5)
const sessionIdText = ref("")
const agentIdText = ref("")

const currentSessionId = ref(null)
const streaming = ref(false)
const references = ref([])
const statusText = ref("")

const messageContainerRef = ref(null)

let typingQueue = []
let typingTimer = null

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false
})

const messages = ref([
  {
    id: Date.now(),
    role: "assistant",
    content:
      "你好，我是人工智能导论课程智能体。请先上传课程资料并构建知识库，然后向我提问。"
  }
])

function getToken() {
  return localStorage.getItem("access_token")
}

function parseNullableNumber(value) {
  if (value === null || value === undefined || value === "") {
    return null
  }

  const numberValue = Number(value)

  if (Number.isNaN(numberValue)) {
    return null
  }

  return numberValue
}

function stopTypingTimer() {
  if (typingTimer) {
    clearInterval(typingTimer)
    typingTimer = null
  }
}

function resetTypingQueue() {
  typingQueue = []
  stopTypingTimer()
}

function enqueueTypingText(text, assistantMessage) {
  if (!text) {
    return
  }

  const chars = Array.from(text)
  typingQueue.push(...chars)

  startTyping(assistantMessage)
}

function startTyping(assistantMessage) {
  if (typingTimer) {
    return
  }

  typingTimer = setInterval(() => {
    if (typingQueue.length === 0) {
      stopTypingTimer()
      return
    }

    // 每次输出 1 个字，演示效果最明显
    const char = typingQueue.shift()
    assistantMessage.content += char

    scrollToBottom()
  }, 35)
}

function waitTypingDone() {
  return new Promise(resolve => {
    const timer = setInterval(() => {
      if (typingQueue.length === 0 && !typingTimer) {
        clearInterval(timer)
        resolve()
      }
    }, 50)
  })
}

function normalizeMarkdown(content) {
  if (!content) {
    return ""
  }

  let text = content

  text = text.replace(/\r\n/g, "\n")

  // 删除空 li，例如 <li><br><br></li>
  text = text.replace(/<li[^>]*>\s*(<br\s*\/?>\s*)+<\/li>/gi, "")

  // 多个 br 压缩为两个换行
  text = text.replace(/(<br\s*\/?>\s*){2,}/gi, "\n\n")

  // 单个 br 转换为换行
  text = text.replace(/<br\s*\/?>/gi, "\n")

  // strong 转 Markdown 加粗
  text = text.replace(/<strong[^>]*>/gi, "**")
  text = text.replace(/<\/strong>/gi, "**")

  // li 转 Markdown 列表
  text = text.replace(/<li[^>]*>/gi, "- ")
  text = text.replace(/<\/li>/gi, "\n")

  // 删除列表外壳
  text = text.replace(/<\/?ul[^>]*>/gi, "")
  text = text.replace(/<\/?ol[^>]*>/gi, "")

  // 删除常见标签
  text = text.replace(/<\/?p[^>]*>/gi, "\n")
  text = text.replace(/<\/?div[^>]*>/gi, "\n")
  text = text.replace(/<\/?span[^>]*>/gi, "")

  // 删除其他 HTML 标签
  text = text.replace(/<\/?[^>]+>/g, "")

  // 把 “1. **标题**” 转成小标题
  text = text.replace(
    /^\s*(\d+)\.\s+\*\*(.+?)\*\*\s*$/gm,
    "### $1. $2"
  )

  // 去掉每行首尾空格
  text = text
    .split("\n")
    .map(line => line.trim())
    .join("\n")

  // 多个空行压缩
  text = text.replace(/\n{3,}/g, "\n\n")

  return text.trim()
}

function renderMarkdown(content) {
  const normalized = normalizeMarkdown(content)
  return md.render(normalized)
}

async function handleSend() {
  const text = question.value.trim()

  if (!text) {
    ElMessage.warning("请输入问题")
    return
  }

  if (streaming.value) {
    ElMessage.warning("当前正在生成，请稍后")
    return
  }

  const token = getToken()

  if (!token) {
    ElMessage.error("请先登录")
    return
  }

  resetTypingQueue()
  statusText.value = ""

  const userMessage = {
    id: Date.now(),
    role: "user",
    content: text
  }

  const assistantMessage = {
    id: Date.now() + 1,
    role: "assistant",
    content: ""
  }

  messages.value.push(userMessage)
  messages.value.push(assistantMessage)

  question.value = ""
  references.value = []
  streaming.value = true

  await scrollToBottom()

  try {
    const payload = {
      question: text,
      session_id: parseNullableNumber(sessionIdText.value) || currentSessionId.value,
      agent_id: parseNullableNumber(agentIdText.value),
      top_k: topK.value
    }

    const response = await fetch("/api/v1/rag/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(errorText || "请求失败")
    }

    if (!response.body) {
      throw new Error("浏览器不支持流式响应")
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder("utf-8")

    let buffer = ""

    while (true) {
      const { value, done } = await reader.read()

      if (done) {
        break
      }

      buffer += decoder.decode(value, {
        stream: true
      })

      const parts = buffer.split("\n\n")
      buffer = parts.pop() || ""

      for (const part of parts) {
        handleSsePart(part, assistantMessage)
      }

      await scrollToBottom()
    }

    // 处理最后可能残留的数据
    if (buffer.trim()) {
      handleSsePart(buffer, assistantMessage)
    }
  } catch (error) {
    console.error(error)
    enqueueTypingText(`\n\n[请求失败] ${error.message || error}`, assistantMessage)
    ElMessage.error("问答失败，请查看后端日志")
  } finally {
    await waitTypingDone()
    streaming.value = false
    statusText.value = ""
    await scrollToBottom()
  }
}

function handleSsePart(part, assistantMessage) {
  const lines = part.split("\n")

  for (const line of lines) {
    // 忽略 SSE comment / padding，例如 ": xxx"
    if (!line.startsWith("data:")) {
      continue
    }

    const jsonText = line.replace("data:", "").trim()

    if (!jsonText) {
      continue
    }

    try {
      const event = JSON.parse(jsonText)

      if (event.type === "session") {
        currentSessionId.value = event.session_id
        sessionIdText.value = String(event.session_id)
      }

      if (event.type === "status") {
        statusText.value = event.message || ""
      }

      if (event.type === "references") {
        references.value = event.data || []
      }

      if (event.type === "delta") {
        enqueueTypingText(event.content || "", assistantMessage)
      }

      if (event.type === "done") {
        if (event.session_id) {
          currentSessionId.value = event.session_id
          sessionIdText.value = String(event.session_id)
        }

        if (event.references) {
          references.value = event.references
        }

        statusText.value = "回答生成完成"
      }

      if (event.type === "error") {
        enqueueTypingText(`\n\n[错误] ${event.message}`, assistantMessage)
      }
    } catch (error) {
      console.error("SSE 解析失败：", error, jsonText)
    }
  }
}

async function scrollToBottom() {
  await nextTick()

  const container = messageContainerRef.value

  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

function clearChat() {
  resetTypingQueue()

  messages.value = [
    {
      id: Date.now(),
      role: "assistant",
      content: "对话已清空。你可以继续向课程智能体提问。"
    }
  ]

  references.value = []
  currentSessionId.value = null
  sessionIdText.value = ""
  statusText.value = ""
  streaming.value = false
}
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 120px);
}

.chat-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 20px;
  height: 100%;
}

.chat-main-panel,
.chat-side-panel {
  border: 1px solid rgba(180, 197, 255, 0.14);
  background: rgba(16, 22, 40, 0.78);
  border-radius: 24px;
  backdrop-filter: blur(18px);
}

.chat-main-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.chat-header {
  padding: 24px 26px 10px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.chat-message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px 26px;
}

.chat-message-row {
  display: flex;
  gap: 14px;
  margin-bottom: 18px;
}

.chat-message-row.user {
  flex-direction: row-reverse;
}

.chat-avatar {
  width: 38px;
  height: 38px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, #6f8cff, #8e63ff);
}

.chat-message-row.assistant .chat-avatar {
  background: linear-gradient(135deg, #20d4fd, #6f8cff);
}

.chat-bubble {
  max-width: 78%;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid rgba(180, 197, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
}

.chat-message-row.user .chat-bubble {
  background: rgba(111, 140, 255, 0.2);
}

.chat-role {
  color: #8fb0ff;
  font-size: 13px;
  font-weight: 760;
  margin-bottom: 8px;
}

.chat-content {
  color: #edf2ff;
  line-height: 1.6;
}

.plain-text {
  white-space: pre-wrap;
  line-height: 1.55;
}

.markdown-body {
  white-space: normal;
  color: #edf2ff;
  line-height: 1.6;
  font-size: 15px;
}

.markdown-body :deep(p) {
  margin: 4px 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  color: #ffffff;
  margin: 10px 0 6px;
  line-height: 1.35;
}

.markdown-body :deep(h1) {
  font-size: 21px;
}

.markdown-body :deep(h2) {
  font-size: 19px;
  border-bottom: 1px solid rgba(180, 197, 255, 0.16);
  padding-bottom: 5px;
}

.markdown-body :deep(h3) {
  font-size: 17px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 22px;
  margin: 4px 0;
}

.markdown-body :deep(li) {
  margin: 2px 0;
  line-height: 1.55;
}

.markdown-body :deep(strong) {
  color: #ffffff;
  font-weight: 800;
}

.typing-indicator {
  color: #8fb0ff;
  font-size: 14px;
  margin: 8px 0 16px 52px;
}

.chat-input-area {
  padding: 18px 26px 24px;
  border-top: 1px solid rgba(180, 197, 255, 0.12);
}

.chat-input-actions {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-tip {
  color: #8793b5;
  font-size: 13px;
}

.chat-side-panel {
  padding: 22px;
  overflow-y: auto;
}

.side-title {
  color: #ffffff;
  font-weight: 800;
  margin-bottom: 14px;
}

.reference-card {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(180, 197, 255, 0.14);
  background: rgba(255, 255, 255, 0.05);
  margin-bottom: 12px;
}

.reference-name {
  color: #ffffff;
  font-weight: 700;
  line-height: 1.5;
}

.reference-id {
  color: #8793b5;
  font-size: 12px;
  margin-top: 6px;
}

.empty-reference {
  color: #8793b5;
  font-size: 14px;
}

.status-line {
  color: #c7d2f0;
  font-size: 14px;
  margin-bottom: 8px;
}

:deep(.el-form-item__label) {
  color: #c7d2f0;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  box-shadow: none;
  border: 1px solid rgba(182, 197, 255, 0.16);
  color: #ffffff;
}

:deep(.el-textarea__inner) {
  color: #ffffff;
}

@media (max-width: 1100px) {
  .chat-shell {
    grid-template-columns: 1fr;
  }

  .chat-side-panel {
    min-height: 300px;
  }
}
</style>