<template>
  <div class="auth-page">
    <div class="auth-left">
      <div class="auth-brand">
        <div class="brand-logo"></div>
        <div class="brand-title">AI Course Agent</div>
      </div>

      <h1 class="auth-slogan">
        面向课程学习的
        <br />
        <span>智能体平台</span>
      </h1>

      <div class="auth-desc">
        集成课程知识库、智能问答、章节考核与学习评价报告，帮助学生围绕课程资料进行精准学习。
      </div>

      <div class="auth-tags">
        <div class="auth-tag">RAG 知识库</div>
        <div class="auth-tag">AI 对话</div>
        <div class="auth-tag">章节考核</div>
        <div class="auth-tag">学习报告</div>
      </div>
    </div>

    <div class="auth-right">
      <div class="auth-card">
        <div class="auth-card-title">欢迎回来</div>
        <div class="auth-card-subtitle">登录你的课程智能体系统</div>

        <el-form
          ref="formRef"
          class="auth-form"
          :model="form"
          :rules="rules"
          label-position="top"
          @keyup.enter="handleLogin"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              size="large"
              placeholder="请输入用户名"
              clearable
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              size="large"
              type="password"
              placeholder="请输入密码"
              show-password
            />
          </el-form-item>

          <el-button
            class="primary-btn"
            type="primary"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form>

        <div class="auth-switch">
          还没有账号？
          <router-link to="/register">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { loginApi, getCurrentUserApi } from "../api/auth"

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: "",
  password: ""
})

const rules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" }
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" }
  ]
}

async function handleLogin() {
  await formRef.value.validate()

  loading.value = true

  try {
    const res = await loginApi(form)

    const token = res.data.token.access_token
    localStorage.setItem("access_token", token)

    const userRes = await getCurrentUserApi()
    localStorage.setItem("user_info", JSON.stringify(userRes.data))

    ElMessage.success("登录成功")
    router.push("/home")
  } finally {
    loading.value = false
  }
}
</script>