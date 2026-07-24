<template>
  <div>
    <div class="page-card">
      <h1 class="page-title">个人中心</h1>
      <div class="page-subtitle">
        查看当前用户信息，修改昵称或密码。
      </div>

      <el-row :gutter="22">
        <el-col :xs="24" :md="10">
          <div class="stat-card">
            <div style="display: flex; align-items: center;">
              <el-avatar
                :size="64"
                style="background: linear-gradient(135deg, #6f8cff, #8e63ff); font-size: 26px;"
              >
                {{ avatarText }}
              </el-avatar>

              <div style="margin-left: 18px;">
                <div style="font-size: 22px; color: #fff; font-weight: 760;">
                  {{ userInfo.nickname || userInfo.username }}
                </div>
                <div style="color: #9ba8c9; margin-top: 6px;">
                  {{ roleText }}
                </div>
              </div>
            </div>

            <el-divider />

            <div style="color: #aeb8d4; line-height: 2;">
              <div>用户ID：{{ userInfo.id }}</div>
              <div>用户名：{{ userInfo.username }}</div>
              <div>账号状态：{{ userInfo.is_active ? "启用" : "禁用" }}</div>
              <div>创建时间：{{ userInfo.created_at }}</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :md="14">
          <el-tabs model-value="info">
            <el-tab-pane label="基本信息" name="info">
              <el-form
                ref="infoFormRef"
                :model="infoForm"
                :rules="infoRules"
                label-width="90px"
              >
                <el-form-item label="昵称" prop="nickname">
                  <el-input
                    v-model="infoForm.nickname"
                    size="large"
                    placeholder="请输入昵称"
                  />
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    :loading="infoLoading"
                    @click="handleUpdateInfo"
                  >
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="修改密码" name="password">
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="90px"
              >
                <el-form-item label="旧密码" prop="old_password">
                  <el-input
                    v-model="passwordForm.old_password"
                    size="large"
                    type="password"
                    show-password
                    placeholder="请输入旧密码"
                  />
                </el-form-item>

                <el-form-item label="新密码" prop="new_password">
                  <el-input
                    v-model="passwordForm.new_password"
                    size="large"
                    type="password"
                    show-password
                    placeholder="请输入新密码"
                  />
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    :loading="passwordLoading"
                    @click="handleUpdatePassword"
                  >
                    修改密码
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue"
import { ElMessage } from "element-plus"
import {
  getCurrentUserApi,
  updateCurrentUserApi,
  updatePasswordApi
} from "../api/auth"

const userInfo = ref({})
const infoFormRef = ref()
const passwordFormRef = ref()
const infoLoading = ref(false)
const passwordLoading = ref(false)

const infoForm = reactive({
  nickname: ""
})

const passwordForm = reactive({
  old_password: "",
  new_password: ""
})

const infoRules = {
  nickname: [
    { required: true, message: "请输入昵称", trigger: "blur" },
    { max: 50, message: "昵称不能超过50位", trigger: "blur" }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: "请输入旧密码", trigger: "blur" }
  ],
  new_password: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 6, max: 50, message: "密码长度为6-50位", trigger: "blur" }
  ]
}

const avatarText = computed(() => {
  const name = userInfo.value.nickname || userInfo.value.username || "U"
  return name.slice(0, 1).toUpperCase()
})

const roleText = computed(() => {
  const role = userInfo.value.role
  if (role === "admin") return "管理员"
  if (role === "teacher") return "教师"
  return "学生"
})

onMounted(async () => {
  await loadUserInfo()
})

async function loadUserInfo() {
  const res = await getCurrentUserApi()
  userInfo.value = res.data
  infoForm.nickname = res.data.nickname || ""
  localStorage.setItem("user_info", JSON.stringify(res.data))
}

async function handleUpdateInfo() {
  await infoFormRef.value.validate()

  infoLoading.value = true

  try {
    const res = await updateCurrentUserApi({
      nickname: infoForm.nickname
    })

    userInfo.value = res.data
    localStorage.setItem("user_info", JSON.stringify(res.data))
    ElMessage.success("用户信息修改成功")
  } finally {
    infoLoading.value = false
  }
}

async function handleUpdatePassword() {
  await passwordFormRef.value.validate()

  passwordLoading.value = true

  try {
    await updatePasswordApi({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })

    passwordForm.old_password = ""
    passwordForm.new_password = ""

    ElMessage.success("密码修改成功")
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style scoped>
:deep(.el-tabs__item) {
  color: #aeb8d4;
}

:deep(.el-tabs__item.is-active) {
  color: #8fb0ff;
}

:deep(.el-tabs__active-bar) {
  background-color: #8fb0ff;
}

:deep(.el-form-item__label) {
  color: #c7d2f0;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  box-shadow: none;
  border: 1px solid rgba(182, 197, 255, 0.16);
}

:deep(.el-input__inner) {
  color: #ffffff;
}

:deep(.el-divider) {
  border-color: rgba(180, 197, 255, 0.14);
}
</style>