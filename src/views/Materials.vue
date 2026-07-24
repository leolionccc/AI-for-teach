<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">课程资料</h1>
          <div class="page-subtitle">
            支持 PDF / Word / PPT 上传与解析，后续将用于 RAG 知识库构建。
          </div>
        </div>

        <el-upload
          :show-file-list="false"
          :before-upload="beforeUpload"
          :disabled="uploading"
        >
          <el-button type="primary" :loading="uploading">
            {{ uploading ? "上传解析中..." : "上传资料" }}
          </el-button>
        </el-upload>
      </div>

      <el-alert
        style="margin-top: 18px;"
        title="如果是扫描版 PDF，可能无法解析出文本，这是正常现象。建议先用小型 DOCX / PPTX 测试上传。"
        type="info"
        show-icon
        :closable="false"
      />

      <el-table
        v-loading="loading"
        :data="tableData"
        class="dark-table"
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="ID" width="70" />

        <el-table-column
          prop="name"
          label="文件名"
          min-width="220"
          show-overflow-tooltip
        />

        <el-table-column prop="file_type" label="类型" width="90">
          <template #default="{ row }">
            <el-tag>{{ row.file_type }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="file_size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatSize(row.file_size) }}
          </template>
        </el-table-column>

        <el-table-column label="解析状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.parse_status)">
              {{ statusText(row.parse_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="上传时间" width="190" />

        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewContent(row)">
              查看内容
            </el-button>

            <el-button size="small" @click="viewParseInfo(row)">
              解析信息
            </el-button>

            <el-button size="small" type="danger" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="contentDialogVisible"
      title="解析内容"
      width="860px"
    >
      <div class="content-box">
        {{ currentContent }}
      </div>
    </el-dialog>

    <el-dialog
      v-model="parseInfoDialogVisible"
      title="解析信息"
      width="680px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="文件名">
          {{ currentRow.name }}
        </el-descriptions-item>

        <el-descriptions-item label="文件类型">
          {{ currentRow.file_type }}
        </el-descriptions-item>

        <el-descriptions-item label="文件大小">
          {{ formatSize(currentRow.file_size) }}
        </el-descriptions-item>

        <el-descriptions-item label="解析状态">
          <el-tag :type="statusType(currentRow.parse_status)">
            {{ statusText(currentRow.parse_status) }}
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="解析说明">
          {{ currentRow.parse_error || "无" }}
        </el-descriptions-item>

        <el-descriptions-item label="服务器文件名">
          {{ currentRow.stored_name }}
        </el-descriptions-item>

        <el-descriptions-item label="文件路径">
          {{ currentRow.file_path }}
        </el-descriptions-item>

        <el-descriptions-item label="上传用户ID">
          {{ currentRow.created_by }}
        </el-descriptions-item>

        <el-descriptions-item label="上传时间">
          {{ currentRow.created_at }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  deleteMaterialApi,
  getMaterialDetailApi,
  listMaterialsApi,
  uploadMaterialApi
} from "../api/material"

const loading = ref(false)
const uploading = ref(false)
const tableData = ref([])

const contentDialogVisible = ref(false)
const parseInfoDialogVisible = ref(false)

const currentContent = ref("")
const currentRow = ref({})

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true

  try {
    const res = await listMaterialsApi()
    tableData.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function beforeUpload(file) {
  const ext = file.name.split(".").pop().toLowerCase()

  if (!["pdf", "docx", "pptx"].includes(ext)) {
    ElMessage.error("只支持 PDF / DOCX / PPTX 文件")
    return false
  }

  const maxSize = 50 * 1024 * 1024

  if (file.size > maxSize) {
    ElMessage.error("文件不能超过 50MB")
    return false
  }

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append("file", file)

    await uploadMaterialApi(formData)

    ElMessage.success("上传成功")
    await loadData()
  } catch (error) {
    console.error(error)
  } finally {
    uploading.value = false
  }

  return false
}

async function viewContent(row) {
  try {
    const res = await getMaterialDetailApi(row.id)
    const detail = res.data || {}
    const content = detail.content || ""

    if (!content) {
      currentContent.value = "暂无解析内容。可能是扫描版 PDF、文件为空，或解析失败。"
    } else {
      currentContent.value = content
    }

    contentDialogVisible.value = true
  } catch (error) {
    console.error(error)
  }
}

function viewParseInfo(row) {
  currentRow.value = row
  parseInfoDialogVisible.value = true
}

async function handleDelete(row) {
  await ElMessageBox.confirm(
    `确定删除文件「${row.name}」吗？`,
    "删除确认",
    {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消"
    }
  )

  await deleteMaterialApi(row.id)

  ElMessage.success("删除成功")
  await loadData()
}

function formatSize(size) {
  if (!size && size !== 0) {
    return "-"
  }

  if (size < 1024) {
    return `${size} B`
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`
  }

  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

function statusText(status) {
  if (status === "success") {
    return "成功"
  }

  if (status === "fail") {
    return "失败"
  }

  if (status === "skipped") {
    return "无文本"
  }

  return status || "-"
}

function statusType(status) {
  if (status === "success") {
    return "success"
  }

  if (status === "fail") {
    return "danger"
  }

  if (status === "skipped") {
    return "warning"
  }

  return "info"
}
</script>

<style scoped>
.content-box {
  max-height: 560px;
  overflow-y: auto;
  white-space: pre-wrap;
  line-height: 1.8;
  color: #303133;
  background: #f7f8fa;
  padding: 16px;
  border-radius: 10px;
}
</style>