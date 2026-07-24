<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">系统日志</h1>
          <div class="page-subtitle">
            查看大模型配置、智能体管理、调用历史等操作记录。
          </div>
        </div>

        <el-button @click="loadData">
          刷新
        </el-button>
      </div>

      <el-form
        :inline="true"
        :model="query"
        style="margin-top: 20px;"
      >
        <el-form-item label="模块">
          <el-input v-model="query.module" placeholder="例如：智能体管理" clearable />
        </el-form-item>

        <el-form-item label="用户名">
          <el-input v-model="query.username" placeholder="请输入用户名" clearable />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="query.log_status" clearable placeholder="全部" style="width: 140px;">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="fail" />
          </el-select>
        </el-form-item>

        <el-form-item label="条数">
          <el-input-number v-model="query.limit" :min="1" :max="500" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadData">
            查询
          </el-button>
          <el-button @click="resetQuery">
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <el-table
        v-loading="loading"
        :data="tableData"
        class="dark-table"
        style="width: 100%; margin-top: 16px;"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="module" label="模块" width="140" />
        <el-table-column prop="action" label="操作" width="160" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="method" label="方法" width="90" />
        <el-table-column prop="path" label="路径" min-width="200" show-overflow-tooltip />

        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="message" label="信息" min-width="220" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="190" />

        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="detailVisible" title="日志详情" width="620px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ detail.id }}</el-descriptions-item>
        <el-descriptions-item label="模块">{{ detail.module }}</el-descriptions-item>
        <el-descriptions-item label="操作">{{ detail.action }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ detail.username }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">{{ detail.method }}</el-descriptions-item>
        <el-descriptions-item label="请求路径">{{ detail.path }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ detail.status }}</el-descriptions-item>
        <el-descriptions-item label="信息">{{ detail.message }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue"
import { getSystemLogDetailApi, listSystemLogsApi } from "../api/systemLog"

const loading = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const detail = ref({})

const query = reactive({
  module: "",
  username: "",
  log_status: "",
  limit: 100
})

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true

  try {
    const params = {
      module: query.module || undefined,
      username: query.username || undefined,
      log_status: query.log_status || undefined,
      limit: query.limit
    }

    const res = await listSystemLogsApi(params)
    tableData.value = res.data || []
  } finally {
    loading.value = false
  }
}

function resetQuery() {
  query.module = ""
  query.username = ""
  query.log_status = ""
  query.limit = 100
  loadData()
}

async function openDetail(row) {
  const res = await getSystemLogDetailApi(row.id)
  detail.value = res.data || {}
  detailVisible.value = true
}
</script>