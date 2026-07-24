<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <div>
          <h1 class="page-title">章节学习路线</h1>
          <div class="page-subtitle">
            学生可在此查看课程章节学习路线和各章节考核配置状态。
          </div>
        </div>

        <el-button @click="loadData">
          刷新
        </el-button>
      </div>

      <el-alert
        style="margin-top: 18px;"
        title="当前阶段仅展示章节路线和配置状态；下一阶段会加入开始考核和逐题答题功能。"
        type="info"
        show-icon
        :closable="false"
      />

      <div v-loading="loading" class="route-container">
        <div
          v-for="(chapter, index) in chapters"
          :key="chapter.id"
          class="route-node"
        >
          <div class="route-index">
            {{ index + 1 }}
          </div>

          <div class="route-content">
            <div class="route-title">
              {{ chapter.title }}
            </div>

            <div class="route-desc">
              {{ chapter.description || "暂无章节说明" }}
            </div>

            <div class="route-meta">
              <el-tag>
                排序：{{ chapter.sort_order }}
              </el-tag>

              <el-tag
                :type="hasConfig(chapter.id) ? 'success' : 'warning'"
              >
                {{ hasConfig(chapter.id) ? "已配置考核" : "未配置考核" }}
              </el-tag>

              <el-tag
                v-if="hasConfig(chapter.id)"
                type="info"
              >
                总题数：{{ getTotalCount(chapter.id) }}
              </el-tag>
            </div>
          </div>
        </div>

        <el-empty
          v-if="!loading && chapters.length === 0"
          description="暂无章节路线"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import {
  listChaptersApi,
  listExamConfigsApi
} from "../../api/examConfig"

const loading = ref(false)
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

function getTotalCount(chapterId) {
  const config = getConfig(chapterId)

  if (!config) {
    return 0
  }

  return (
    Number(config.choice_count || 0) +
    Number(config.judge_count || 0) +
    Number(config.short_answer_count || 0)
  )
}
</script>

<style scoped>
.route-container {
  margin-top: 24px;
}

.route-node {
  position: relative;
  display: flex;
  gap: 18px;
  margin-bottom: 22px;
}

.route-node::before {
  content: "";
  position: absolute;
  left: 22px;
  top: 48px;
  bottom: -22px;
  width: 2px;
  background: rgba(180, 197, 255, 0.18);
}

.route-node:last-child::before {
  display: none;
}

.route-index {
  width: 46px;
  height: 46px;
  border-radius: 16px;
  background: linear-gradient(135deg, #6f8cff, #8e63ff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 900;
  flex-shrink: 0;
  box-shadow: 0 12px 30px rgba(111, 140, 255, 0.25);
}

.route-content {
  flex: 1;
  padding: 18px 20px;
  border-radius: 20px;
  border: 1px solid rgba(180, 197, 255, 0.14);
  background: rgba(255, 255, 255, 0.055);
}

.route-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: 800;
  margin-bottom: 8px;
}

.route-desc {
  color: #aeb8d4;
  line-height: 1.7;
  margin-bottom: 12px;
}

.route-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>