<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">考试记录</h1>
          <div class="page-subtitle">
            查看当前用户的章节考核记录。本阶段展示得分和状态，学习报告将在下一阶段生成。
          </div>
        </div>

        <div class="header-actions">
          <el-button @click="loadData">
            刷新
          </el-button>

          <el-button type="primary" @click="router.push('/exam/start')">
            开始新考核
          </el-button>
        </div>
      </div>

      <el-alert
        style="margin-top: 18px;"
        type="info"
        show-icon
        :closable="false"
        title="本阶段提交考试后会汇总客观题得分；简答题评价和学习报告将在下一阶段完成。"
      />

      <el-table
        v-loading="loading"
        :data="records"
        class="dark-table"
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="考试ID" width="90" />

        <el-table-column prop="chapter_id" label="章节ID" width="90" />

        <el-table-column prop="config_id" label="配置ID" width="90" />

        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'submitted' ? 'success' : 'warning'">
              {{ row.status === "submitted" ? "已提交" : "进行中" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="total_score" label="当前得分" width="110">
          <template #default="{ row }">
            <span class="score-text">
              {{ row.total_score || 0 }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="开始时间" min-width="180" />

        <el-table-column prop="updated_at" label="更新时间" min-width="180" />

        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'submitted'"
              size="small"
              type="primary"
              @click="continueExam(row)"
            >
              继续答题
            </el-button>

            <el-button
              v-if="row.status === 'submitted'"
              size="small"
              type="success"
              @click="viewReport(row)"
            >
              查看报告
            </el-button>

            <el-button
              size="small"
              @click="viewQuestions(row)"
            >
              查看题目
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty
        v-if="!loading && records.length === 0"
        description="暂无考试记录"
      />
    </div>

    <el-dialog
      v-model="questionDialogVisible"
      title="考试题目预览"
      width="860px"
    >
      <div v-loading="questionLoading">
        <div
          v-for="(question, index) in previewQuestions"
          :key="question.id"
          class="preview-question"
        >
          <div class="preview-header">
            <span class="preview-index">
              第 {{ index + 1 }} 题
            </span>

            <el-tag>
              {{ questionTypeText(question.question_type) }}
            </el-tag>

            <el-tag type="success">
              {{ question.score }} 分
            </el-tag>
          </div>

          <div class="preview-text">
            {{ question.question_text }}
          </div>

          <div
            v-if="question.options && question.options.length"
            class="preview-options"
          >
            <div
              v-for="option in question.options"
              :key="option"
              class="preview-option"
            >
              {{ option }}
            </div>
          </div>
        </div>

        <el-empty
          v-if="!questionLoading && previewQuestions.length === 0"
          description="暂无题目"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import {
  listExamQuestionsApi,
  listExamRecordsApi
} from "../../api/examRuntime"

const router = useRouter()

const loading = ref(false)
const records = ref([])

const questionDialogVisible = ref(false)
const questionLoading = ref(false)
const previewQuestions = ref([])

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true

  try {
    const res = await listExamRecordsApi()
    records.value = res.data || []
  } finally {
    loading.value = false
  }
}

function continueExam(row) {
  router.push(`/exam/do/${row.id}`)
}

async function viewQuestions(row) {
  questionDialogVisible.value = true
  questionLoading.value = true
  previewQuestions.value = []

  try {
    const res = await listExamQuestionsApi(row.id)
    previewQuestions.value = res.data || []
  } finally {
    questionLoading.value = false
  }
}

function questionTypeText(type) {
  if (type === "choice") {
    return "选择题"
  }

  if (type === "judge") {
    return "判断题"
  }

  if (type === "short_answer") {
    return "简答题"
  }

  return type
}

function viewReport(row) {
  router.push(`/exam/report/${row.id}`)
}
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 10px;
}

.score-text {
  color: #ffffff;
  font-weight: 800;
}

/* =========================
   考试题目预览弹窗
   ========================= */

.preview-question {
  padding: 20px 22px;
  border-radius: 18px;
  border: 1px solid rgba(180, 197, 255, 0.18);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.075), rgba(255, 255, 255, 0.035)),
    rgba(15, 23, 42, 0.88);
  margin-bottom: 18px;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18);
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.preview-index {
  color: #ffffff;
  font-weight: 900;
  font-size: 17px;
  letter-spacing: 0.2px;
}

.preview-text {
  color: #ffffff;
  line-height: 1.85;
  margin-bottom: 14px;
  font-size: 16px;
  font-weight: 650;
}

.preview-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.preview-option {
  color: #edf2ff;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(111, 140, 255, 0.11);
  border: 1px solid rgba(180, 197, 255, 0.16);
  line-height: 1.65;
  font-size: 15px;
}

.preview-option:hover {
  background: rgba(111, 140, 255, 0.18);
  border-color: rgba(180, 197, 255, 0.28);
}

/* 弹窗内部整体颜色增强 */
:deep(.el-dialog) {
  background: rgba(15, 23, 42, 0.96);
  border: 1px solid rgba(180, 197, 255, 0.18);
  border-radius: 20px;
}

:deep(.el-dialog__title) {
  color: #ffffff;
  font-weight: 800;
}

:deep(.el-dialog__body) {
  color: #edf2ff;
}

:deep(.el-table) {
  color: #edf2ff;
}
</style>

