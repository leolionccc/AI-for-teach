<template>
  <div class="auth-page">
    <div class="auth-left">
      <div class="auth-brand">
        <div class="brand-logo"></div>
        <div class="brand-title">AI Course Agent</div>
      </div>

      <h1 class="auth-slogan">
        构建你的
        <br />
        <span>课程智能助手</span>
      </h1>

      <div class="auth-desc">
        注册后即可进入系统，后续可以上传课程资料、构建知识库、进行智能问答和章节测试。
      </div>

      <div class="auth-tags">
        <div class="auth-tag">Vue3</div>
        <div class="auth-tag">FastAPI</div>
        <div class="auth-tag">JWT</div>
        <div class="auth-tag">SQLite</div>
      </div>
    </div>

    <div class="auth-right">
      <div class="auth-card">
        <div class="auth-card-title">创建账号</div>
        <div class="auth-card-subtitle">开始使用课程智能体系统</div>

        <el-form
          ref="formRef"
          class="auth-form"
          :model="form"
          :rules="rules"
          label-position="top"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              size="large"
              placeholder="请输入用户名，至少3位"
              clearable
            />
          </el-form-item>

          <el-form-item label="昵称" prop="nickname">
            <el-input
              v-model="form.nickname"
              size="large"
              placeholder="请输入昵称"
              clearable
            />
          </el-form-item>

          <el-form-item label="角色" prop="role">
            <el-select
              v-model="form.role"
              size="large"
              style="width: 100%"
            >
              <el-option label="学生" value="student" />
              <el-option label="教师" value="teacher" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              size="large"
              type="password"
              placeholder="请输入密码，至少6位"
              show-password
            />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              size="large"
              type="password"
              placeholder="请再次输入密码"
              show-password
            />
          </el-form-item>

          <el-button
            class="primary-btn"
            type="primary"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form>

        <div class="auth-switch">
          已有账号？
          <router-link to="/login">返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { registerApi } from "../api/auth"

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: "",
  nickname: "",
  role: "student",
  password: "",
  confirmPassword: ""
})

function validateConfirmPassword(rule, value, callback) {
  if (!value) {
    callback(new Error("请确认密码"))
  } else if (value !== form.password) {
    callback(new Error("两次输入的密码不一致"))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 50, message: "用户名长度为3-50位", trigger: "blur" }
  ],
  nickname: [
    { max: 50, message: "昵称不能超过50位", trigger: "blur" }
  ],
  role: [
    { required: true, message: "请选择角色", trigger: "change" }
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 50, message: "密码长度为6-50位", trigger: "blur" }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: "blur" }
  ]
}

async function handleRegister() {
  await formRef.value.validate()

  loading.value = true

  try {
    await registerApi({
      username: form.username,
      password: form.password,
      nickname: form.nickname,
      role: form.role
    })

    ElMessage.success("注册成功，请登录")
    router.push("/login")
  } finally {
    loading.value = false
  }
}
</script>