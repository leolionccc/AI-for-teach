<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">智能体管理</h1>
          <div class="page-subtitle">
            配置课程智能体名称、介绍、系统提示词和欢迎语。
          </div>
        </div>

        <el-button type="primary" @click="openCreateDialog">
          新增智能体
        </el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="tableData"
        class="dark-table"
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="智能体名称" min-width="180" />
        <el-table-column prop="description" label="介绍" min-width="240" show-overflow-tooltip />
        <el-table-column prop="welcome_message" label="欢迎语" min-width="220" show-overflow-tooltip />

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled ? 'success' : 'info'">
              {{ row.is_enabled ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="190" />

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑智能体' : '新增智能体'"
      width="760px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
      >
        <el-form-item label="智能体名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：人工智能导论课程助手" />
        </el-form-item>

        <el-form-item label="智能体介绍">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入智能体介绍"
          />
        </el-form-item>

        <el-form-item label="系统提示词" prop="system_prompt">
          <el-input
            v-model="form.system_prompt"
            type="textarea"
            :rows="7"
            placeholder="请输入系统提示词"
          />
        </el-form-item>

        <el-form-item label="欢迎语">
          <el-input
            v-model="form.welcome_message"
            type="textarea"
            :rows="3"
            placeholder="请输入欢迎语"
          />
        </el-form-item>

        <el-form-item label="头像地址">
          <el-input v-model="form.avatar" placeholder="可为空" />
        </el-form-item>

        <el-form-item label="是否启用">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">
          取消
        </el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  createAgentApi,
  deleteAgentApi,
  listAgentsApi,
  updateAgentApi
} from "../api/agent"

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const formRef = ref()
const tableData = ref([])

const form = reactive({
  name: "",
  description: "",
  system_prompt: "",
  welcome_message: "",
  avatar: "",
  is_enabled: true
})

const rules = {
  name: [{ required: true, message: "请输入智能体名称", trigger: "blur" }],
  system_prompt: [{ required: true, message: "请输入系统提示词", trigger: "blur" }]
}

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const res = await listAgentsApi()
    tableData.value = res.data || []
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ""
  form.description = ""
  form.system_prompt =
    "你是人工智能导论课程学习助手，请基于课程资料回答学生问题，回答要准确、清晰、适合教学场景。"
  form.welcome_message = "你好，我是人工智能导论课程助手，可以帮你解答课程问题。"
  form.avatar = ""
  form.is_enabled = true
}

function openCreateDialog() {
  isEdit.value = false
  currentId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  currentId.value = row.id

  form.name = row.name
  form.description = row.description || ""
  form.system_prompt = row.system_prompt || ""
  form.welcome_message = row.welcome_message || ""
  form.avatar = row.avatar || ""
  form.is_enabled = row.is_enabled

  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitLoading.value = true

  try {
    const payload = {
      name: form.name,
      description: form.description,
      system_prompt: form.system_prompt,
      welcome_message: form.welcome_message,
      avatar: form.avatar,
      is_enabled: form.is_enabled
    }

    if (isEdit.value) {
      await updateAgentApi(currentId.value, payload)
      ElMessage.success("修改成功")
    } else {
      await createAgentApi(payload)
      ElMessage.success("创建成功")
    }

    dialogVisible.value = false
    loadData()
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(
    `确定删除智能体「${row.name}」吗？`,
    "删除确认",
    {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消"
    }
  )

  await deleteAgentApi(row.id)
  ElMessage.success("删除成功")
  loadData()
}
</script>