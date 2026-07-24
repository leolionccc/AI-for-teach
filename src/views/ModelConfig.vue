<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">大模型配置</h1>
          <div class="page-subtitle">
            管理 OpenAI、Qwen、DeepSeek 或自定义模型配置，当前阶段只保存配置，不实际调用模型。
          </div>
        </div>

        <el-button type="primary" @click="openCreateDialog">
          新增配置
        </el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="tableData"
        class="dark-table"
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="配置名称" min-width="160" />
        <el-table-column prop="provider" label="供应商" width="120" />
        <el-table-column prop="model_name" label="模型名称" min-width="160" />
        <el-table-column prop="api_base_url" label="API地址" min-width="200" />
        <el-table-column prop="api_key_masked" label="API Key" min-width="150" />
        <el-table-column prop="temperature" label="温度" width="90" />
        <el-table-column prop="max_tokens" label="最大Token" width="110" />

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? "已启用" : "未启用" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button
              size="small"
              type="success"
              :disabled="row.is_active"
              @click="handleActivate(row)"
            >
              启用
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑大模型配置' : '新增大模型配置'"
      width="620px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
      >
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：DeepSeek 默认配置" />
        </el-form-item>

        <el-form-item label="供应商" prop="provider">
          <el-select v-model="form.provider" style="width: 100%">
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="Qwen" value="qwen" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>

        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="form.model_name" placeholder="例如：deepseek-chat" />
        </el-form-item>

        <el-form-item label="API地址">
          <el-input v-model="form.api_base_url" placeholder="例如：https://api.deepseek.com" />
        </el-form-item>

        <el-form-item label="API Key">
          <el-input
            v-model="form.api_key"
            type="password"
            show-password
            placeholder="请输入 API Key"
          />
        </el-form-item>

        <el-form-item label="温度参数">
          <el-input v-model="form.temperature" placeholder="0.7" />
        </el-form-item>

        <el-form-item label="最大Token">
          <el-input-number
            v-model="form.max_tokens"
            :min="1"
            :max="100000"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="是否启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
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
  activateModelConfigApi,
  createModelConfigApi,
  deleteModelConfigApi,
  listModelConfigsApi,
  updateModelConfigApi
} from "../api/modelConfig"

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const formRef = ref()
const tableData = ref([])

const form = reactive({
  name: "",
  provider: "deepseek",
  model_name: "",
  api_base_url: "",
  api_key: "",
  temperature: "0.7",
  max_tokens: 2048,
  is_active: false,
  remark: ""
})

const rules = {
  name: [{ required: true, message: "请输入配置名称", trigger: "blur" }],
  provider: [{ required: true, message: "请选择供应商", trigger: "change" }],
  model_name: [{ required: true, message: "请输入模型名称", trigger: "blur" }]
}

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const res = await listModelConfigsApi()
    tableData.value = res.data || []
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ""
  form.provider = "deepseek"
  form.model_name = ""
  form.api_base_url = ""
  form.api_key = ""
  form.temperature = "0.7"
  form.max_tokens = 2048
  form.is_active = false
  form.remark = ""
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
  form.provider = row.provider
  form.model_name = row.model_name
  form.api_base_url = row.api_base_url || ""
  form.api_key = ""
  form.temperature = row.temperature
  form.max_tokens = row.max_tokens
  form.is_active = row.is_active
  form.remark = row.remark || ""

  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()

  submitLoading.value = true

  try {
    const payload = {
      name: form.name,
      provider: form.provider,
      model_name: form.model_name,
      api_base_url: form.api_base_url,
      api_key: form.api_key || undefined,
      temperature: form.temperature,
      max_tokens: form.max_tokens,
      is_active: form.is_active,
      remark: form.remark
    }

    if (isEdit.value) {
      await updateModelConfigApi(currentId.value, payload)
      ElMessage.success("修改成功")
    } else {
      await createModelConfigApi(payload)
      ElMessage.success("创建成功")
    }

    dialogVisible.value = false
    loadData()
  } finally {
    submitLoading.value = false
  }
}

async function handleActivate(row) {
  await activateModelConfigApi(row.id)
  ElMessage.success("启用成功")
  loadData()
}

async function handleDelete(row) {
  await ElMessageBox.confirm(
    `确定删除配置「${row.name}」吗？`,
    "删除确认",
    {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消"
    }
  )

  await deleteModelConfigApi(row.id)
  ElMessage.success("删除成功")
  loadData()
}
</script>