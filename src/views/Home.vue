<template>
  <div>
    <div class="page-card">
      <h1 class="page-title">欢迎使用 AI 课程智能体系统</h1>
      <div class="page-subtitle">
        你已完成登录认证流程。下一阶段可以继续开发大模型配置、智能体管理、调用历史和系统日志。
      </div>

      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-label">当前用户</div>
          <div class="stat-value">{{ userInfo.nickname || userInfo.username }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">用户角色</div>
          <div class="stat-value">{{ roleText }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">登录状态</div>
          <div class="stat-value">已认证</div>
        </div>
      </div>
    </div>

    <div class="page-card" style="margin-top: 22px;">
      <h2 style="margin-top: 0; color: #fff;">后续功能规划</h2>

      <el-timeline>
        <el-timeline-item timestamp="第三阶段" placement="top">
          大模型配置、智能体管理、调用历史、系统日志
        </el-timeline-item>
        <el-timeline-item timestamp="第四阶段" placement="top">
          课程资料上传、PDF Word PPT 解析
        </el-timeline-item>
        <el-timeline-item timestamp="第五阶段" placement="top">
          RAG 知识库构建、智能体问答、SSE 流式输出
        </el-timeline-item>
        <el-timeline-item timestamp="第六阶段" placement="top">
          章节考核、自动评分、学习评价报告
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import { getCurrentUserApi } from "../api/auth"

const userInfo = ref({})

const roleText = computed(() => {
  const role = userInfo.value.role
  if (role === "admin") return "管理员"
  if (role === "teacher") return "教师"
  return "学生"
})

onMounted(async () => {
  const res = await getCurrentUserApi()
  userInfo.value = res.data
  localStorage.setItem("user_info", JSON.stringify(res.data))
})
</script>