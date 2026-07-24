<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">知识库构建</h1>
          <div class="page-subtitle">
            将已上传并解析成功的课程资料构建为 Chroma 向量知识库，供智能体问答使用。
          </div>
        </div>

        <el-button
          type="primary"
          :loading="buildingAll"
          @click="handleBuildAll"
        >
          构建全部资料索引
        </el-button>
      </div>

      <el-alert
        style="margin-top: 18px;"
        title="请先在“课程资料”页面上传并解析资料，再来这里构建知识库。扫描版 PDF 可能没有文本内容，无法构建索引。"
        type="info"
        show-icon
        :closable="false"
      />

      <el-table
        v-loading="loading"
        :data="materials"
        class="dark-table"
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="ID" width="70" />

        <el-table-column
          prop="name"
          label="资料名称"
          min-width="240"
          show-overflow-tooltip
        />

        <el-table-column prop="file_type" label="类型" width="90">
          <template #default="{ row }">
            <el-tag>{{ row.file_type }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatSize(row.file_size) }}
          </template>
        </el-table-column>

        <el-table-column label="解析状态" width="120">
          <template #default="{ row }">
            <el-tag :type="parseStatusType(row.parse_status)">
              {{ parseStatusText(row.parse_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="上传时间" width="190" />

        <el-table-column label="操作" width="190" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              :loading="buildingId === row.id"
              :disabled="row.parse_status !== 'success'"
              @click="handleBuildOne(row)"
            >
              构建索引
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="page-card" style="margin-top: 22px;">
      <h2 style="margin-top: 0; color: #fff;">RAG 检索测试</h2>
      <div class="page-subtitle">
        输入一个课程问题，测试当前知识库是否能检索出相关资料片段。
      </div>

      <el-form :model="searchForm" label-width="90px">
        <el-form-item label="问题">
          <el-input
            v-model="searchForm.query"
            placeholder="例如：什么是人工智能？"
            clearable
          />
        </el-form-item>

        <el-form-item label="返回数量">
          <el-input-number
            v-model="searchForm.top_k"
            :min="1"
            :max="20"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="searchLoading"
            @click="handleSearch"
          >
            检索
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="searchResults.length > 0" class="search-result-list">
        <div
          v-for="(item, index) in searchResults"
          :key="index"
          class="search-result-item"
        >
          <div class="search-result-title">
            片段 {{ index + 1 }} / {{ item.material_name }}
          </div>

          <div class="search-result-meta">
            material_id: {{ item.material_id }}，
            chunk_index: {{ item.chunk_index }}，
            distance: {{ formatDistance(item.distance) }}
          </div>

          <div class="search-result-content">
            {{ item.content }}
          </div>
        </div>
      </div>

      <el-empty
        v-else-if="searched"
        description="没有检索到相关内容"
      />
    </div>

    <el-dialog
      v-model="buildResultVisible"
      title="构建结果"
      width="760px"
    >
      <pre class="json-box">{{ JSON.stringify(buildResult, null, 2) }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue"
import { ElMessage } from "element-plus"
import { listMaterialsApi } from "../api/material"
import {
  buildAllMaterialIndexesApi,
  buildMaterialIndexApi,
  ragSearchApi
} from "../api/rag"

const loading = ref(false)
const materials = ref([])

const buildingAll = ref(false)
const buildingId = ref(null)

const buildResultVisible = ref(false)
const buildResult = ref({})

const searchLoading = ref(false)
const searched = ref(false)
const searchResults = ref([])

const searchForm = reactive({
  query: "",
  top_k: 5
})

onMounted(() => {
  loadMaterials()
})

async function loadMaterials() {
  loading.value = true

  try {
    const res = await listMaterialsApi()
    materials.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleBuildOne(row) {
  buildingId.value = row.id

  try {
    const res = await buildMaterialIndexApi({
      material_id: row.id
    })

    buildResult.value = res.data || {}
    buildResultVisible.value = true

    ElMessage.success("构建成功")
  } finally {
    buildingId.value = null
  }
}

async function handleBuildAll() {
  buildingAll.value = true

  try {
    const res = await buildAllMaterialIndexesApi()

    buildResult.value = res.data || {}
    buildResultVisible.value = true

    ElMessage.success("构建完成")
  } finally {
    buildingAll.value = false
  }
}

async function handleSearch() {
  if (!searchForm.query.trim()) {
    ElMessage.warning("请输入检索问题")
    return
  }

  searchLoading.value = true
  searched.value = true
  searchResults.value = []

  try {
    const res = await ragSearchApi({
      query: searchForm.query,
      top_k: searchForm.top_k
    })

    searchResults.value = res.data || []
  } finally {
    searchLoading.value = false
  }
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

function parseStatusText(status) {
  if (status === "success") return "成功"
  if (status === "fail") return "失败"
  if (status === "skipped") return "无文本"
  return status || "-"
}

function parseStatusType(status) {
  if (status === "success") return "success"
  if (status === "fail") return "danger"
  if (status === "skipped") return "warning"
  return "info"
}

function formatDistance(distance) {
  if (distance === null || distance === undefined) {
    return "-"
  }

  return Number(distance).toFixed(4)
}
</script>

<style scoped>
.search-result-list {
  margin-top: 20px;
}

.search-result-item {
  margin-bottom: 16px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(180, 197, 255, 0.14);
  background: rgba(255, 255, 255, 0.045);
}

.search-result-title {
  color: #ffffff;
  font-weight: 760;
  margin-bottom: 8px;
}

.search-result-meta {
  color: #8793b5;
  font-size: 13px;
  margin-bottom: 10px;
}

.search-result-content {
  color: #dce5ff;
  white-space: pre-wrap;
  line-height: 1.8;
}

.json-box {
  max-height: 500px;
  overflow-y: auto;
  background: #111827;
  color: #d1d5db;
  padding: 16px;
  border-radius: 10px;
}
</style>