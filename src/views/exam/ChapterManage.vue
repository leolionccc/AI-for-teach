<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">章节管理</h1>
          <div class="page-subtitle">
            教师可在此维护课程章节，后续章节考核将基于这些章节进行配置。
          </div>
        </div>

        <el-button type="primary" @click="openCreateDialog">
          新增章节
        </el-button>
      </div>

      <el-alert
        style="margin-top: 18px;"
        title="建议按照课程教学顺序设置排序，例如第一章 sort_order=1，第二章 sort_order=2。"
        type="info"
        show-icon
        :closable="false"
      />

      <el-table
        v-loading="loading"
        :data="chapters"
        class="dark-table"
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="ID" width="70" />

        <el-table-column prop="title" label="章节标题" min-width="220" />

        <el-table-column
          prop="description"
          label="章节说明"
          min-width="300"
          show-overflow-tooltip
        />

        <el-table-column prop="sort_order" label="排序" width="90" />

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

      <el-empty
        v-if="!loading && chapters.length === 0"
        description="暂无章节，请先新增章节"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑章节' : '新增章节'"
      width="620px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="章节标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="例如：第五章 AVL 树"
          />
        </el-form-item>

        <el-form-item label="章节说明">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入章节说明，例如：学习 AVL 树的定义、平衡调整和旋转操作。"
          />
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number
            v-model="form.sort_order"
            :min="0"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="handleSubmit"
        >
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
  createChapterApi,
  deleteChapterApi,
  listChaptersApi,
  updateChapterApi
} from "../../api/examConfig"

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const formRef = ref()

const chapters = ref([])

const form = reactive({
  title: "",
  description: "",
  sort_order: 0
})

const rules = {
  title: [
    { required: true, message: "请输入章节标题", trigger: "blur" }
  ]
}

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true

  try {
    const res = await listChaptersApi()
    chapters.value = res.data || []
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.title = ""
  form.description = ""
  form.sort_order = 0
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

  form.title = row.title
  form.description = row.description || ""
  form.sort_order = row.sort_order || 0

  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()

  submitLoading.value = true

  try {
    const payload = {
      title: form.title,
      description: form.description,
      sort_order: form.sort_order
    }

    if (isEdit.value) {
      await updateChapterApi(currentId.value, payload)
      ElMessage.success("修改成功")
    } else {
      await createChapterApi(payload)
      ElMessage.success("创建成功")
    }

    dialogVisible.value = false
    await loadData()
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(
    `确定删除章节「${row.title}」吗？`,
    "删除确认",
    {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消"
    }
  )

  await deleteChapterApi(row.id)
  ElMessage.success("删除成功")
  await loadData()
}
</script>