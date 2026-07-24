<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">开始章节考核</h1>
          <div class="page-subtitle">
            选择一个已配置考核规则的章节，系统将自动生成题目并进入逐题答题。
          </div>
        </div>

        <el-button @click="loadData">
          刷新
        </el-button>
      </div>

      <el-alert
        style="margin-top: 18px;"
        title="请先在“章节管理”和“考核配置”中完成章节与题型配置，否则无法开始考核。"
        type="info"
        show-icon
        :closable="false"
      />

      <div v-loading="loading" class="chapter-grid">
        <div
          v-for="chapter in chapters"
          :key="chapter.id"
          class="chapter-card"
        >
          <div class="chapter-card-header">
            <div>
              <div class="chapter-title">
                {{ chapter.title }}
              </div>
              <div class="chapter-desc">
                {{ chapter.description || "暂无章节说明" }}
              </div>
            </div>

            <el-tag :type="hasConfig(chapter.id) ? 'success' : 'warning'">
              {{ hasConfig(chapter.id) ? "已配置" : "未配置" }}
            </el-tag>
          </div>

          <div v-if="getConfig(chapter.id)" class="config-info">
            <div>知识点：{{ getConfig(chapter.id).knowledge_points }}</div>
            <div>
              选择题 {{ getConfig(chapter.id).choice_count }} /
              判断题 {{ getConfig(chapter.id).judge_count }} /
              简答题 {{ getConfig(chapter.id).short_answer_count }}
            </div>
            <div>总分：{{ getConfig(chapter.id).total_score }}</div>
          </div>

          <div v-else class="config-info muted">
            该章节暂无考核配置，请先前往“考核配置”页面创建。
          </div>

          <el-button
            type="primary"
            style="width: 100%; margin-top: 18px;"
            :disabled="!hasConfig(chapter.id)"
            :loading="startingChapterId === chapter.id"
            @click="handleStart(chapter)"
          >
            开始考核
          </el-button>
        </div>

        <el-empty
          v-if="!loading && chapters.length === 0"
          description="暂无章节"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import {
  listChaptersApi,
  listExamConfigsApi
} from "../../api/examConfig"
import { startExamApi } from "../../api/examRuntime"

const router = useRouter()

const loading = ref(false)
const startingChapterId = ref(null)
const chapters = ref([])
const configs = ref([])

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true

  try {
    const chapterRes = await listChaptersApi()
    const configRes = await listExamConfigsApi()

    chapters.value = chapterRes.data || []
    configs.value = configRes.data || []
  } finally {
    loading.value = false
  }
}

function getConfig(chapterId) {
  return configs.value.find(item => item.chapter_id === chapterId)
}

function hasConfig(chapterId) {
  return Boolean(getConfig(chapterId))
}

async function handleStart(chapter) {
  const config = getConfig(chapter.id)

  if (!config) {
    ElMessage.warning("该章节暂无考核配置")
    return
  }

  startingChapterId.value = chapter.id

  try {
    const res = await startExamApi({
      chapter_id: chapter.id,
      config_id: config.id
    })

    const exam = res.data

    ElMessage.success("考试已开始")
    router.push(`/exam/do/${exam.id}`)
  } finally {
    startingChapterId.value = null
  }
}
</script>

<style scoped>
.chapter-grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 18px;
}

.chapter-card {
  padding: 22px;
  border-radius: 22px;
  border: 1px solid rgba(180, 197, 255, 0.14);
  background: rgba(255, 255, 255, 0.055);
}

.chapter-card-header {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.chapter-title {
  color: #ffffff;
  font-weight: 800;
  font-size: 19px;
  margin-bottom: 8px;
}

.chapter-desc {
  color: #aeb8d4;
  line-height: 1.7;
  min-height: 56px;
}

.config-info {
  margin-top: 14px;
  color: #c7d2f0;
  line-height: 1.8;
  font-size: 14px;
}

.config-info.muted {
  color: #8793b5;
}
</style>
