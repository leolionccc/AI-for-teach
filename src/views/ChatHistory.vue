<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">调用历史</h1>
          <div class="page-subtitle">
            当前阶段用于管理对话会话和消息记录，后续智能体问答会自动写入这里。
          </div>
        </div>

        <el-button type="primary" @click="openCreateSessionDialog">
          新建会话
        </el-button>
      </div>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :xs="24" :md="8">
          <div class="mini-panel">
            <div class="mini-panel-title">会话列表</div>

            <el-scrollbar height="560px">
              <div
                v-for="item in sessions"
                :key="item.id"
                class="session-item"
                :class="{ active: currentSession && currentSession.id === item.id }"
                @click="selectSession(item)"
              >
                <div class="session-title">{{ item.title }}</div>
                <div class="session-time">{{ item.created_at }}</div>

                <div class="session-actions">
                  <el-button size="small" text @click.stop="openRenameDialog(item)">
                    重命名
                  </el-button>
                  <el-button size="small" text type="danger" @click.stop="deleteSession(item)">
                    删除
                  </el-button>
                </div>
              </div>
            </el-scrollbar>
          </div>
        </el-col>

        <el-col :xs="24" :md="16">
          <div class="mini-panel">
            <div class="mini-panel-title">
              消息记录
              <span v-if="currentSession" style="color: #8f9bbb; font-size: 13px;">
                / {{ currentSession.title }}
              </span>
            </div>

            <div v-if="!currentSession" class="empty-tip">
              请选择左侧会话
            </div>

            <template v-else>
              <el-scrollbar height="440px">
                <div
                  v-for="msg in messages"
                  :key="msg.id"
                  class="message-item"
                  :class="msg.role"
                >
                  <div class="message-role">
                    {{ roleText(msg.role) }}
                  </div>
                  <div class="message-content">
                    {{ msg.content }}
                  </div>
                  <div class="message-meta">
                    {{ msg.model_name || "-" }} / {{ msg.created_at }}
                  </div>
                </div>
              </el-scrollbar>

              <el-divider />

              <el-form
                ref="msgFormRef"
                :model="msgForm"
                :rules="msgRules"
                label-width="80px"
              >
                <el-form-item label="角色" prop="role">
                  <el-select v-model="msgForm.role" style="width: 160px;">
                    <el-option label="用户" value="user" />
                    <el-option label="助手" value="assistant" />
                    <el-option label="系统" value="system" />
                  </el-select>
                </el-form-item>

                <el-form-item label="内容" prop="content">
                  <el-input
                    v-model="msgForm.content"
                    type="textarea"
                    :rows="3"
                    placeholder="当前阶段可以手动添加测试消息"
                  />
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" @click="createMessage">
                    添加消息
                  </el-button>
                </el-form-item>
              </el-form>
            </template>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="sessionDialogVisible" title="新建会话" width="480px">
      <el-form ref="sessionFormRef" :model="sessionForm" :rules="sessionRules" label-width="90px">
        <el-form-item label="会话标题" prop="title">
          <el-input v-model="sessionForm.title" placeholder="请输入会话标题" />
        </el-form-item>

        <el-form-item label="智能体ID">
          <el-input-number v-model="sessionForm.agent_id" :min="1" style="width: 100%;" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="sessionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createSession">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="renameDialogVisible" title="重命名会话" width="480px">
      <el-input v-model="renameTitle" placeholder="请输入新的会话标题" />

      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="renameSession">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  createChatMessageApi,
  createChatSessionApi,
  deleteChatSessionApi,
  listChatMessagesApi,
  listChatSessionsApi,
  updateChatSessionApi
} from "../api/chatHistory"

const sessions = ref([])
const messages = ref([])
const currentSession = ref(null)

const sessionDialogVisible = ref(false)
const renameDialogVisible = ref(false)

const sessionFormRef = ref()
const msgFormRef = ref()

const renameId = ref(null)
const renameTitle = ref("")

const sessionForm = reactive({
  title: "新的课程问答",
  agent_id: 1
})

const msgForm = reactive({
  role: "user",
  content: "",
  model_name: "deepseek-chat",
  token_count: 0
})

const sessionRules = {
  title: [{ required: true, message: "请输入会话标题", trigger: "blur" }]
}

const msgRules = {
  role: [{ required: true, message: "请选择角色", trigger: "change" }],
  content: [{ required: true, message: "请输入消息内容", trigger: "blur" }]
}

onMounted(() => {
  loadSessions()
})

async function loadSessions() {
  const res = await listChatSessionsApi()
  sessions.value = res.data || []
}

function openCreateSessionDialog() {
  sessionForm.title = "新的课程问答"
  sessionForm.agent_id = 1
  sessionDialogVisible.value = true
}

async function createSession() {
  await sessionFormRef.value.validate()

  const res = await createChatSessionApi({
    title: sessionForm.title,
    agent_id: sessionForm.agent_id
  })

  ElMessage.success("创建成功")
  sessionDialogVisible.value = false
  await loadSessions()
  selectSession(res.data)
}

async function selectSession(item) {
  currentSession.value = item
  const res = await listChatMessagesApi(item.id)
  messages.value = res.data || []
}

function openRenameDialog(item) {
  renameId.value = item.id
  renameTitle.value = item.title
  renameDialogVisible.value = true
}

async function renameSession() {
  if (!renameTitle.value) {
    ElMessage.warning("请输入会话标题")
    return
  }

  await updateChatSessionApi(renameId.value, {
    title: renameTitle.value
  })

  ElMessage.success("修改成功")
  renameDialogVisible.value = false
  await loadSessions()

  if (currentSession.value && currentSession.value.id === renameId.value) {
    currentSession.value.title = renameTitle.value
  }
}

async function deleteSession(item) {
  await ElMessageBox.confirm(
    `确定删除会话「${item.title}」吗？`,
    "删除确认",
    {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消"
    }
  )

  await deleteChatSessionApi(item.id)
  ElMessage.success("删除成功")

  if (currentSession.value && currentSession.value.id === item.id) {
    currentSession.value = null
    messages.value = []
  }

  loadSessions()
}

async function createMessage() {
  if (!currentSession.value) {
    ElMessage.warning("请先选择会话")
    return
  }

  await msgFormRef.value.validate()

  await createChatMessageApi(currentSession.value.id, {
    role: msgForm.role,
    content: msgForm.content,
    model_name: msgForm.model_name,
    token_count: msgForm.content.length
  })

  msgForm.content = ""
  ElMessage.success("添加成功")
  selectSession(currentSession.value)
}

function roleText(role) {
  if (role === "assistant") return "助手"
  if (role === "system") return "系统"
  return "用户"
}
</script>