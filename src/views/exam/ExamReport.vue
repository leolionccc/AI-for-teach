<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">学习评价报告</h1>
          <div class="page-subtitle">
            查看章节考核结果、知识掌握情况、答题明细和复习建议。
          </div>
        </div>

        <div class="header-actions">
          <el-button @click="router.push('/exam/records')">
            返回考试记录
          </el-button>

          <el-button type="primary" @click="loadReport">
            刷新报告
          </el-button>
        </div>
      </div>

      <div v-loading="loading" class="report-layout">
        <div class="report-main">
          <div class="score-summary">
            <div class="score-card">
              <div class="score-label">本次得分</div>
              <div class="score-value">
                {{ exam.total_score || 0 }}
              </div>
              <div class="score-unit">分</div>
            </div>

            <div class="summary-card">
              <div class="summary-row">
                <span>考试ID</span>
                <strong>{{ exam.id || "-" }}</strong>
              </div>

              <div class="summary-row">
                <span>章节ID</span>
                <strong>{{ exam.chapter_id || "-" }}</strong>
              </div>

              <div class="summary-row">
                <span>配置ID</span>
                <strong>{{ exam.config_id || "-" }}</strong>
              </div>

              <div class="summary-row">
                <span>状态</span>
                <el-tag :type="exam.status === 'submitted' ? 'success' : 'warning'">
                  {{ exam.status === "submitted" ? "已提交" : "进行中" }}
                </el-tag>
              </div>

              <div class="summary-row">
                <span>提交时间</span>
                <strong>{{ exam.updated_at || "-" }}</strong>
              </div>
            </div>
          </div>

          <div class="report-section">
            <div class="section-title">学习评价报告</div>

            <div
              class="report-content markdown-body"
              v-html="renderMarkdown(exam.report || '暂无学习评价报告')"
            ></div>
          </div>
        </div>

        <div class="report-side">
          <div class="side-title">答题统计</div>

          <div class="side-line">
            <span>总题数</span>
            <strong>{{ answers.length }}</strong>
          </div>

          <div class="side-line">
            <span>选择题</span>
            <strong>{{ typeCount.choice }}</strong>
          </div>

          <div class="side-line">
            <span>判断题</span>
            <strong>{{ typeCount.judge }}</strong>
          </div>

          <div class="side-line">
            <span>简答题</span>
            <strong>{{ typeCount.short_answer }}</strong>
          </div>

          <el-divider />

          <div class="side-title">得分概览</div>

          <div class="side-line">
            <span>已得分</span>
            <strong>{{ exam.total_score || 0 }}</strong>
          </div>

          <div class="side-line">
            <span>题目总分</span>
            <strong>{{ totalQuestionScore }}</strong>
          </div>

          <el-progress
            :percentage="scorePercent"
            :stroke-width="10"
            style="margin-top: 14px;"
          />
        </div>
      </div>
    </div>

    <div class="page-card" style="margin-top: 22px;">
      <div class="page-header">
        <div>
          <h2 class="sub-title">答题明细</h2>
          <div class="page-subtitle">
            查看每道题的标准答案、学生答案、得分和反馈。
          </div>
        </div>
      </div>

      <div v-loading="loading" class="answer-list">
        <div
          v-for="(item, index) in answers"
          :key="item.question_id"
          class="answer-card"
        >
          <div class="answer-header">
            <div class="answer-index">
              第 {{ index + 1 }} 题
            </div>

            <el-tag>{{ questionTypeText(item.question_type) }}</el-tag>

            <el-tag type="info">
              满分 {{ item.question_score }} 分
            </el-tag>

            <el-tag :type="scoreTagType(item)">
              得分 {{ item.student_score || 0 }} 分
            </el-tag>
          </div>

          <div class="answer-question">
            {{ item.question_text }}
          </div>

          <div
            v-if="item.options && item.options.length"
            class="answer-options"
          >
            <div
              v-for="option in item.options"
              :key="option"
              class="answer-option"
            >
              {{ option }}
            </div>
          </div>

          <div class="answer-grid">
            <div class="answer-block">
              <div class="block-title">学生答案</div>
              <div class="block-content student-answer">
                {{ item.student_answer || "未作答" }}
              </div>
            </div>

            <div class="answer-block">
              <div class="block-title">标准答案</div>
              <div class="block-content standard-answer">
                {{ item.standard_answer || "-" }}
              </div>
            </div>
          </div>

          <div v-if="item.analysis" class="analysis-box">
            <div class="block-title">题目解析</div>
            <div class="block-content">
              {{ item.analysis }}
            </div>
          </div>

          <div v-if="item.feedback" class="feedback-box">
            <div class="block-title">评价反馈</div>
            <div class="block-content">
              {{ item.feedback }}
            </div>
          </div>
        </div>

        <el-empty
          v-if="!loading && answers.length === 0"
          description="暂无答题明细"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import MarkdownIt from "markdown-it"
import { ElMessage } from "element-plus"
import { getExamReportApi } from "../../api/examRuntime"

const route = useRoute()
const router = useRouter()

const examId = Number(route.params.examId)

const loading = ref(false)
const exam = ref({})
const answers = ref([])

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false
})

const totalQuestionScore = computed(() => {
  const total = answers.value.reduce((sum, item) => {
    return sum + Number(item.question_score || 0)
  }, 0)

  return Number(total.toFixed(2))
})

const scorePercent = computed(() => {
  if (!totalQuestionScore.value) {
    return 0
  }

  return Math.round((Number(exam.value.total_score || 0) / totalQuestionScore.value) * 100)
})

const typeCount = computed(() => {
  const result = {
    choice: 0,
    judge: 0,
    short_answer: 0
  }

  answers.value.forEach(item => {
    if (result[item.question_type] !== undefined) {
      result[item.question_type] += 1
    }
  })

  return result
})

onMounted(() => {
  loadReport()
})

async function loadReport() {
  loading.value = true

  try {
    const res = await getExamReportApi(examId)
    const data = res.data || {}

    exam.value = data.exam || {}
    answers.value = data.answers || []
  } catch (error) {
    console.error(error)
    ElMessage.error("加载学习报告失败")
  } finally {
    loading.value = false
  }
}

function normalizeMarkdown(content) {
  if (!content) {
    return ""
  }

  let text = content

  text = text.replace(/\r\n/g, "\n")
  text = text.replace(/<br\s*\/?>/gi, "\n")
  text = text.replace(/<strong[^>]*>/gi, "**")
  text = text.replace(/<\/strong>/gi, "**")
  text = text.replace(/<\/?ul[^>]*>/gi, "")
  text = text.replace(/<\/?ol[^>]*>/gi, "")
  text = text.replace(/<li[^>]*>/gi, "- ")
  text = text.replace(/<\/li>/gi, "\n")
  text = text.replace(/<\/?p[^>]*>/gi, "\n")
  text = text.replace(/<\/?div[^>]*>/gi, "\n")
  text = text.replace(/<\/?span[^>]*>/gi, "")
  text = text.replace(/<\/?[^>]+>/g, "")
  text = text.replace(/\n{3,}/g, "\n\n")

  return text.trim()
}

function renderMarkdown(content) {
  return md.render(normalizeMarkdown(content))
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

function scoreTagType(item) {
  const score = Number(item.student_score || 0)
  const fullScore = Number(item.question_score || 0)

  if (fullScore <= 0) {
    return "info"
  }

  const ratio = score / fullScore

  if (ratio >= 0.8) {
    return "success"
  }

  if (ratio >= 0.5) {
    return "warning"
  }

  return "danger"
}
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 10px;
}

.sub-title {
  margin: 0;
  color: #ffffff;
  font-size: 22px;
  font-weight: 900;
}

.report-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 22px;
  margin-top: 24px;
}

.report-main,
.report-side {
  border-radius: 24px;
  border: 1px solid rgba(180, 197, 255, 0.16);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.035)),
    rgba(15, 23, 42, 0.76);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.18);
}

.report-main {
  padding: 24px;
}

.report-side {
  padding: 22px;
  height: fit-content;
}

.score-summary {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 18px;
  margin-bottom: 22px;
}

.score-card {
  padding: 24px;
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(111, 140, 255, 0.35), rgba(142, 99, 255, 0.22));
  border: 1px solid rgba(180, 197, 255, 0.18);
}

.score-label {
  color: #c7d2f0;
  font-size: 14px;
  margin-bottom: 10px;
}

.score-value {
  color: #ffffff;
  font-size: 52px;
  font-weight: 950;
  line-height: 1;
}

.score-unit {
  color: #dce5ff;
  margin-top: 8px;
}

.summary-card {
  padding: 22px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(180, 197, 255, 0.13);
}

.summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #c7d2f0;
  margin-bottom: 12px;
}

.summary-row strong {
  color: #ffffff;
}

.report-section {
  padding: 22px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(180, 197, 255, 0.12);
}

.section-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: 900;
  margin-bottom: 16px;
}

.report-content {
  color: #edf2ff;
}

.side-title {
  color: #ffffff;
  font-size: 16px;
  font-weight: 900;
  margin-bottom: 14px;
}

.side-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #c7d2f0;
  margin-bottom: 10px;
}

.side-line strong {
  color: #ffffff;
}

.answer-list {
  margin-top: 22px;
}

.answer-card {
  padding: 22px;
  border-radius: 22px;
  border: 1px solid rgba(180, 197, 255, 0.16);
  background:
    linear-gradient(135deg, rgba(111, 140, 255, 0.08), rgba(142, 99, 255, 0.04)),
    rgba(255, 255, 255, 0.045);
  margin-bottom: 18px;
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.answer-index {
  color: #ffffff;
  font-size: 18px;
  font-weight: 900;
}

.answer-question {
  color: #ffffff;
  line-height: 1.85;
  font-size: 16px;
  font-weight: 650;
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(180, 197, 255, 0.12);
}

.answer-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.answer-option {
  color: #edf2ff;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(111, 140, 255, 0.1);
  border: 1px solid rgba(180, 197, 255, 0.14);
}

.answer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 14px;
}

.answer-block,
.analysis-box,
.feedback-box {
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(180, 197, 255, 0.12);
}

.analysis-box,
.feedback-box {
  margin-top: 14px;
}

.block-title {
  color: #8fb0ff;
  font-weight: 850;
  margin-bottom: 8px;
}

.block-content {
  color: #edf2ff;
  line-height: 1.75;
  white-space: pre-wrap;
}

.student-answer {
  color: #ffffff;
}

.standard-answer {
  color: #b7f7cb;
}

.feedback-box {
  background: rgba(111, 140, 255, 0.08);
}

.markdown-body {
  color: #edf2ff;
  line-height: 1.7;
  font-size: 15px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  color: #ffffff;
  margin: 12px 0 8px;
  line-height: 1.35;
}

.markdown-body :deep(h1) {
  font-size: 24px;
}

.markdown-body :deep(h2) {
  font-size: 21px;
  border-bottom: 1px solid rgba(180, 197, 255, 0.16);
  padding-bottom: 6px;
}

.markdown-body :deep(h3) {
  font-size: 18px;
}

.markdown-body :deep(p) {
  margin: 6px 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 22px;
  margin: 8px 0;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.markdown-body :deep(strong) {
  color: #ffffff;
  font-weight: 900;
}

@media (max-width: 1100px) {
  .report-layout {
    grid-template-columns: 1fr;
  }

  .score-summary {
    grid-template-columns: 1fr;
  }

  .answer-grid {
    grid-template-columns: 1fr;
  }
}
</style>