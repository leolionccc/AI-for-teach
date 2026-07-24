<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">章节考核答题</h1>
          <div class="page-subtitle">
            当前为逐题答题模式，请保存当前题答案后进入下一题。
          </div>
        </div>

        <el-button
          type="success"
          :loading="submitLoading"
          @click="handleSubmitExam"
        >
          提交考试
        </el-button>
      </div>

      <el-alert
        style="margin-top: 18px;"
        type="info"
        show-icon
        :closable="false"
        title="选择题可直接选择选项；判断题选择正确或错误；简答题请输入完整回答。"
      />

      <div v-loading="loading" class="exam-layout">
        <div class="question-main">
          <template v-if="currentQuestion">
            <div class="progress-bar">
              <div>
                第 {{ currentIndex + 1 }} / {{ questions.length }} 题
              </div>

              <el-progress
                :percentage="progressPercent"
                :stroke-width="10"
                style="width: 240px;"
              />
            </div>

            <div class="question-card">
              <div class="question-header">
                <div class="question-index">
                  第 {{ currentIndex + 1 }} 题
                </div>

                <el-tag>
                  {{ questionTypeText(currentQuestion.question_type) }}
                </el-tag>

                <el-tag type="success">
                  {{ currentQuestion.score }} 分
                </el-tag>

                <el-tag :type="savedMap[currentQuestion.id] ? 'success' : 'warning'">
                  {{ savedMap[currentQuestion.id] ? "已保存" : "未保存" }}
                </el-tag>
              </div>

              <div class="question-text">
                {{ currentQuestion.question_text }}
              </div>

              <!-- 选择题 / 判断题选项 -->
              <div
                v-if="currentQuestion.options && currentQuestion.options.length"
                class="question-options"
              >
                <el-radio-group
                  v-if="currentQuestion.question_type === 'choice'"
                  v-model="answerMap[currentQuestion.id]"
                  class="option-radio-group"
                  @change="handleAnswerChanged(currentQuestion.id)"
                >
                  <el-radio
                    v-for="option in currentQuestion.options"
                    :key="option"
                    :label="extractChoiceValue(option)"
                    class="option-radio"
                  >
                    {{ option }}
                  </el-radio>
                </el-radio-group>

                <el-radio-group
                  v-else-if="currentQuestion.question_type === 'judge'"
                  v-model="answerMap[currentQuestion.id]"
                  class="option-radio-group"
                  @change="handleAnswerChanged(currentQuestion.id)"
                >
                  <el-radio
                    v-for="option in currentQuestion.options"
                    :key="option"
                    :label="option"
                    class="option-radio"
                  >
                    {{ option }}
                  </el-radio>
                </el-radio-group>

                <div v-else>
                  <div
                    v-for="option in currentQuestion.options"
                    :key="option"
                    class="option-item"
                  >
                    {{ option }}
                  </div>
                </div>
              </div>

              <!-- 简答题 -->
              <el-input
                v-if="currentQuestion.question_type === 'short_answer'"
                v-model="answerMap[currentQuestion.id]"
                type="textarea"
                :rows="8"
                resize="none"
                placeholder="请输入你的简答题答案"
                @input="handleAnswerChanged(currentQuestion.id)"
              />

              <!-- 选择/判断题备用输入 -->
              <el-input
                v-else
                v-model="answerMap[currentQuestion.id]"
                type="textarea"
                :rows="3"
                resize="none"
                placeholder="也可以手动输入答案，例如：B 或 正确"
                @input="handleAnswerChanged(currentQuestion.id)"
              />

              <div class="question-actions">
                <el-button
                  :disabled="currentIndex === 0"
                  @click="prevQuestion"
                >
                  上一题
                </el-button>

                <el-button
                  type="primary"
                  :loading="answerLoading"
                  @click="saveCurrentAnswer"
                >
                  保存本题
                </el-button>

                <el-button
                  v-if="currentIndex < questions.length - 1"
                  type="primary"
                  :loading="nextLoading"
                  @click="saveAndNext"
                >
                  保存并下一题
                </el-button>

                <el-button
                  v-else
                  type="success"
                  :loading="submitLoading"
                  @click="handleSubmitExam"
                >
                  提交考试
                </el-button>
              </div>
            </div>
          </template>

          <el-empty
            v-else-if="!loading"
            description="暂无题目"
          />
        </div>

        <div class="question-side">
          <div class="side-title">题号导航</div>

          <div class="question-nav">
            <button
              v-for="(question, index) in questions"
              :key="question.id"
              class="question-nav-item"
              :class="{
                active: index === currentIndex,
                saved: savedMap[question.id],
                answered: hasAnswer(question.id) && !savedMap[question.id]
              }"
              @click="goQuestion(index)"
            >
              {{ index + 1 }}
            </button>
          </div>

          <el-divider />

          <div class="side-title">答题进度</div>

          <div class="side-line">
            总题数：{{ questions.length }}
          </div>

          <div class="side-line">
            已填写：{{ answeredCount }}
          </div>

          <div class="side-line">
            已保存：{{ savedCount }}
          </div>

          <div class="side-line">
            未保存：{{ questions.length - savedCount }}
          </div>

          <el-progress
            :percentage="saveProgressPercent"
            :stroke-width="10"
            style="margin-top: 14px;"
          />

          <el-divider />

          <div class="side-title">操作提示</div>

          <div class="side-tip">
            1. 每一题都可以单独保存。
          </div>
          <div class="side-tip">
            2. 切换题目不会自动保存，请点击保存。
          </div>
          <div class="side-tip">
            3. 提交考试后不能继续修改答案。
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  listExamQuestionsApi,
  submitExamAnswerApi,
  submitExamApi
} from "../../api/examRuntime"

const route = useRoute()
const router = useRouter()

const examId = Number(route.params.examId)

const loading = ref(false)
const answerLoading = ref(false)
const nextLoading = ref(false)
const submitLoading = ref(false)

const questions = ref([])
const currentIndex = ref(0)

const answerMap = reactive({})
const savedMap = reactive({})

const currentQuestion = computed(() => {
  return questions.value[currentIndex.value] || null
})

const progressPercent = computed(() => {
  if (questions.value.length === 0) {
    return 0
  }

  return Math.round(((currentIndex.value + 1) / questions.value.length) * 100)
})

const answeredCount = computed(() => {
  return questions.value.filter(item => hasAnswer(item.id)).length
})

const savedCount = computed(() => {
  return questions.value.filter(item => savedMap[item.id]).length
})

const saveProgressPercent = computed(() => {
  if (questions.value.length === 0) {
    return 0
  }

  return Math.round((savedCount.value / questions.value.length) * 100)
})

onMounted(() => {
  loadQuestions()
})

async function loadQuestions() {
  loading.value = true

  try {
    const res = await listExamQuestionsApi(examId)
    questions.value = res.data || []

    questions.value.forEach(question => {
      if (answerMap[question.id] === undefined) {
        answerMap[question.id] = ""
      }

      if (savedMap[question.id] === undefined) {
        savedMap[question.id] = false
      }
    })
  } finally {
    loading.value = false
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

function extractChoiceValue(option) {
  if (!option) {
    return ""
  }

  const text = String(option).trim()

  if (/^[A-Da-d][.．、\s]/.test(text)) {
    return text.slice(0, 1).toUpperCase()
  }

  return text
}

function hasAnswer(questionId) {
  return Boolean(String(answerMap[questionId] || "").trim())
}

function handleAnswerChanged(questionId) {
  savedMap[questionId] = false
}

async function saveCurrentAnswer() {
  const question = currentQuestion.value

  if (!question) {
    return false
  }

  const answerText = String(answerMap[question.id] || "").trim()

  if (!answerText) {
    ElMessage.warning("请输入当前题答案")
    return false
  }

  answerLoading.value = true

  try {
    await submitExamAnswerApi(examId, {
      question_id: question.id,
      answer_text: answerText
    })

    savedMap[question.id] = true
    ElMessage.success("本题答案已保存")

    return true
  } finally {
    answerLoading.value = false
  }
}

async function saveAndNext() {
  nextLoading.value = true

  try {
    const success = await saveCurrentAnswer()

    if (!success) {
      return
    }

    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value += 1
    }
  } finally {
    nextLoading.value = false
  }
}

function prevQuestion() {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1
  }
}

function goQuestion(index) {
  currentIndex.value = index
}

async function handleSubmitExam() {
  if (questions.value.length === 0) {
    ElMessage.warning("当前没有题目")
    return
  }

  if (currentQuestion.value) {
    const answerText = String(answerMap[currentQuestion.value.id] || "").trim()

    if (answerText && !savedMap[currentQuestion.value.id]) {
      await saveCurrentAnswer()
    }
  }

  const unsavedCount = questions.value.length - savedCount.value
  const unansweredCount = questions.value.length - answeredCount.value

  let confirmMessage = "确定提交考试吗？提交后将不能继续答题。"

  if (unansweredCount > 0 || unsavedCount > 0) {
    confirmMessage = `还有 ${unansweredCount} 道题未填写，${unsavedCount} 道题未保存，确定提交考试吗？`
  }

  await ElMessageBox.confirm(
    confirmMessage,
    "提交确认",
    {
      type: "warning",
      confirmButtonText: "提交",
      cancelButtonText: "取消"
    }
  )

  submitLoading.value = true

  try {
    await submitExamApi(examId)
    ElMessage.success("考试提交成功，学习报告已生成")
    router.push(`/exam/report/${examId}`)
  } finally {
    submitLoading.value = false
  }
}
</script>
<style scoped>
/* =========================
   整体布局
   ========================= */

.exam-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 22px;
  margin-top: 24px;
}

.question-main,
.question-side {
  border-radius: 24px;
  border: 1px solid rgba(180, 197, 255, 0.16);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.035)),
    rgba(15, 23, 42, 0.76);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.18);
}

.question-main {
  padding: 24px;
  min-height: 560px;
}

.question-side {
  padding: 22px;
  height: fit-content;
  position: sticky;
  top: 20px;
}

/* =========================
   顶部进度
   ========================= */

.progress-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #dce5ff;
  margin-bottom: 20px;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(111, 140, 255, 0.09);
  border: 1px solid rgba(180, 197, 255, 0.13);
  font-weight: 700;
}

/* =========================
   题目卡片
   ========================= */

.question-card {
  padding: 24px;
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(111, 140, 255, 0.09), rgba(142, 99, 255, 0.05)),
    rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(180, 197, 255, 0.16);
}

.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.question-index {
  color: #ffffff;
  font-size: 21px;
  font-weight: 900;
  margin-right: 6px;
  letter-spacing: 0.2px;
}

.question-text {
  color: #ffffff;
  font-size: 17px;
  font-weight: 650;
  line-height: 1.9;
  margin-bottom: 20px;
  padding: 16px 18px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(180, 197, 255, 0.12);
}

/* =========================
   选项样式
   ========================= */

.question-options {
  margin-bottom: 18px;
}

.option-radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-radio {
  min-height: 46px;
  padding: 12px 14px;
  margin-right: 0;
  border-radius: 14px;
  background: rgba(111, 140, 255, 0.09);
  border: 1px solid rgba(180, 197, 255, 0.14);
  color: #edf2ff;
  transition: all 0.2s ease;
}

.option-radio:hover {
  background: rgba(111, 140, 255, 0.16);
  border-color: rgba(180, 197, 255, 0.26);
  transform: translateY(-1px);
}

.option-item {
  color: #edf2ff;
  margin: 8px 0;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(111, 140, 255, 0.11);
  border: 1px solid rgba(180, 197, 255, 0.14);
}

/* =========================
   操作按钮
   ========================= */

.question-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

/* =========================
   右侧题号导航
   ========================= */

.side-title {
  color: #ffffff;
  font-weight: 900;
  font-size: 16px;
  margin-bottom: 14px;
}

.question-nav {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.question-nav-item {
  width: 100%;
  height: 42px;
  border-radius: 14px;
  border: 1px solid rgba(180, 197, 255, 0.18);
  background: rgba(255, 255, 255, 0.055);
  color: #c7d2f0;
  cursor: pointer;
  font-weight: 800;
  box-shadow: inset 0 0 0 1px transparent;
  transition: all 0.2s ease;
}

.question-nav-item:hover {
  color: #ffffff;
  background: rgba(111, 140, 255, 0.18);
  border-color: rgba(180, 197, 255, 0.32);
  transform: translateY(-1px);
}

/* 当前题 */
.question-nav-item.active {
  color: #ffffff;
  background: linear-gradient(135deg, #6f8cff, #8e63ff);
  border-color: rgba(255, 255, 255, 0.28);
  box-shadow: 0 10px 24px rgba(111, 140, 255, 0.34);
}

/* 已保存 */
.question-nav-item.saved {
  color: #ffffff;
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.55), rgba(55, 184, 120, 0.35));
  border-color: rgba(103, 194, 58, 0.85);
}

/* 已填写但未保存 */
.question-nav-item.answered {
  color: #ffffff;
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.52), rgba(245, 108, 108, 0.28));
  border-color: rgba(230, 162, 60, 0.85);
}

/* 当前题优先级最高 */
.question-nav-item.active.saved,
.question-nav-item.active.answered {
  background: linear-gradient(135deg, #6f8cff, #8e63ff);
  border-color: rgba(255, 255, 255, 0.32);
}

/* =========================
   右侧进度信息
   ========================= */

.side-line {
  color: #dce5ff;
  margin-bottom: 9px;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
}

.side-tip {
  color: #aeb8d4;
  font-size: 13px;
  line-height: 1.75;
  margin-bottom: 7px;
  padding-left: 2px;
}

/* =========================
   Element Plus 输入区域适配暗色
   ========================= */

:deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.075);
  border-radius: 14px;
  box-shadow: none;
  border: 1px solid rgba(182, 197, 255, 0.18);
  color: #ffffff;
  line-height: 1.75;
}

:deep(.el-textarea__inner::placeholder) {
  color: #8f9abb;
}

:deep(.el-radio) {
  color: #edf2ff;
}

:deep(.el-radio__label) {
  color: #edf2ff;
  font-weight: 600;
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  color: #ffffff;
}

:deep(.el-progress__text) {
  color: #dce5ff;
}

/* =========================
   响应式
   ========================= */

@media (max-width: 1100px) {
  .exam-layout {
    grid-template-columns: 1fr;
  }

  .question-side {
    position: static;
  }

  .question-nav {
    grid-template-columns: repeat(8, 1fr);
  }
}

@media (max-width: 640px) {
  .progress-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .question-nav {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
