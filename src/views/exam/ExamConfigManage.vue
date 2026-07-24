<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">考核配置</h1>
          <div class="page-subtitle">
            为章节配置知识点、题型数量、总分和学习评价维度。
          </div>
        </div>

        <el-button type="primary" @click="openCreateDialog">
          新增配置
        </el-button>
      </div>

      <el-alert
        style="margin-top: 18px;"
        title="示例：章节：第五章；知识点：AVL树；选择题2；判断题2；简答题2；总题数6。"
        type="info"
        show-icon
        :closable="false"
      />

      <el-form
        :inline="true"
        style="margin-top: 20px;"
      >
        <el-form-item label="章节">
          <el-select
            v-model="queryChapterId"
            placeholder="全部章节"
            clearable
            style="width: 280px;"
            @change="loadConfigs"
          >
            <el-option
              v-for="chapter in chapters"
              :key="chapter.id"
              :label="chapter.title"
              :value="chapter.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button @click="loadConfigs">
            查询
          </el-button>
        </el-form-item>
      </el-form>

      <el-table
        v-loading="loading"
        :data="configs"
        class="dark-table"
        style="width: 100%; margin-top: 10px;"
      >
        <el-table-column prop="id" label="ID" width="70" />

        <el-table-column label="章节" min-width="200">
          <template #default="{ row }">
            {{ getChapterName(row.chapter_id) }}
          </template>
        </el-table-column>

        <el-table-column
          prop="knowledge_points"
          label="知识点"
          min-width="280"
          show-overflow-tooltip
        />

        <el-table-column prop="choice_count" label="选择题" width="90" />
        <el-table-column prop="judge_count" label="判断题" width="90" />
        <el-table-column prop="short_answer_count" label="简答题" width="90" />

        <el-table-column label="总题数" width="90">
          <template #default="{ row }">
            {{ row.choice_count + row.judge_count + row.short_answer_count }}
          </template>
        </el-table-column>

        <el-table-column prop="total_score" label="总分" width="90" />

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
        v-if="!loading && configs.length === 0"
        description="暂无考核配置"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑考核配置' : '新增考核配置'"
      width="760px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="章节" prop="chapter_id">
          <el-select
            v-model="form.chapter_id"
            placeholder="请选择章节"
            style="width: 100%;"
            :disabled="isEdit"
          >
            <el-option
              v-for="chapter in chapters"
              :key="chapter.id"
              :label="chapter.title"
              :value="chapter.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="知识点" prop="knowledge_points">
          <el-input
            v-model="form.knowledge_points"
            type="textarea"
            :rows="4"
            placeholder="例如：AVL树、平衡因子、左旋、右旋、LR旋转、RL旋转"
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="选择题">
              <el-input-number
                v-model="form.choice_count"
                :min="0"
                :max="50"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="判断题">
              <el-input-number
                v-model="form.judge_count"
                :min="0"
                :max="50"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="简答题">
              <el-input-number
                v-model="form.short_answer_count"
                :min="0"
                :max="50"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="总题数">
          <el-tag type="success">
            {{ totalQuestionCount }} 题
          </el-tag>
        </el-form-item>

        <el-form-item label="总分">
          <el-input-number
            v-model="form.total_score"
            :min="1"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="评价维度">
          <el-input
            v-model="form.evaluation_dimensions"
            type="textarea"
            :rows="3"
            placeholder="知识掌握情况、基础概念掌握、综合分析能力、建议复习知识点"
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
import { computed, onMounted, reactive, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  createExamConfigApi,
  deleteExamConfigApi,
  listChaptersApi,
  listExamConfigsApi,
  updateExamConfigApi
} from "../../api/examConfig"

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const formRef = ref()

const chapters = ref([])
const configs = ref([])
const queryChapterId = ref(null)

const form = reactive({
  chapter_id: null,
  knowledge_points: "",
  choice_count: 2,
  judge_count: 2,
  short_answer_count: 2,
  total_score: 100,
  evaluation_dimensions: "知识掌握情况、基础概念掌握、综合分析能力、建议复习知识点"
})

const totalQuestionCount = computed(() => {
  return (
    Number(form.choice_count || 0) +
    Number(form.judge_count || 0) +
    Number(form.short_answer_count || 0)
  )
})

const rules = {
  chapter_id: [
    { required: true, message: "请选择章节", trigger: "change" }
  ],
  knowledge_points: [
    { required: true, message: "请输入知识点", trigger: "blur" }
  ]
}

onMounted(async () => {
  await loadChapters()
  await loadConfigs()
})

async function loadChapters() {
  const res = await listChaptersApi()
  chapters.value = res.data || []
}

async function loadConfigs() {
  loading.value = true

  try {
    const params = {}

    if (queryChapterId.value) {
      params.chapter_id = queryChapterId.value
    }

    const res = await listExamConfigsApi(params)
    configs.value = res.data || []
  } finally {
    loading.value = false
  }
}

function getChapterName(chapterId) {
  const chapter = chapters.value.find(item => item.id === chapterId)
  return chapter ? chapter.title : `章节 ${chapterId}`
}

function resetForm() {
  form.chapter_id = null
  form.knowledge_points = ""
  form.choice_count = 2
  form.judge_count = 2
  form.short_answer_count = 2
  form.total_score = 100
  form.evaluation_dimensions = "知识掌握情况、基础概念掌握、综合分析能力、建议复习知识点"
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

  form.chapter_id = row.chapter_id
  form.knowledge_points = row.knowledge_points
  form.choice_count = row.choice_count
  form.judge_count = row.judge_count
  form.short_answer_count = row.short_answer_count
  form.total_score = row.total_score
  form.evaluation_dimensions = row.evaluation_dimensions || ""

  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()

  if (totalQuestionCount.value <= 0) {
    ElMessage.warning("题目总数必须大于 0")
    return
  }

  submitLoading.value = true

  try {
    if (isEdit.value) {
      const payload = {
        knowledge_points: form.knowledge_points,
        choice_count: form.choice_count,
        judge_count: form.judge_count,
        short_answer_count: form.short_answer_count,
        total_score: form.total_score,
        evaluation_dimensions: form.evaluation_dimensions
      }

      await updateExamConfigApi(currentId.value, payload)
      ElMessage.success("修改成功")
    } else {
      const payload = {
        chapter_id: form.chapter_id,
        knowledge_points: form.knowledge_points,
        choice_count: form.choice_count,
        judge_count: form.judge_count,
        short_answer_count: form.short_answer_count,
        total_score: form.total_score,
        evaluation_dimensions: form.evaluation_dimensions
      }

      await createExamConfigApi(payload)
      ElMessage.success("创建成功")
    }

    dialogVisible.value = false
    await loadConfigs()
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(
    `确定删除该考核配置吗？`,
    "删除确认",
    {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消"
    }
  )

  await deleteExamConfigApi(row.id)
  ElMessage.success("删除成功")
  await loadConfigs()
}
</script>