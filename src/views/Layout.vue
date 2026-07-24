<template>
  <el-container class="app-layout">
    <el-aside width="248px" class="app-aside">
      <div class="sidebar-brand">
        <div class="sidebar-logo"></div>
        <div>AI课程智能体</div>
      </div>

      <el-menu
        class="sidebar-menu"
        :default-active="activeMenu"
        router
      >
        <el-menu-item index="/home">
          <el-icon><House /></el-icon>
          <span>工作台</span>
        </el-menu-item>

        <el-menu-item index="/model-config">
          <el-icon><Setting /></el-icon>
          <span>大模型配置</span>
        </el-menu-item>

        <el-menu-item index="/agents">
          <el-icon><Cpu /></el-icon>
          <span>智能体管理</span>
        </el-menu-item>

        <el-menu-item index="/chat-history">
          <el-icon><ChatDotRound /></el-icon>
          <span>调用历史</span>
        </el-menu-item>

        <el-menu-item index="/materials">
          <el-icon><FolderOpened /></el-icon>
          <span>课程资料</span>
        </el-menu-item>

         <el-menu-item index="/knowledge-base">
           <el-icon><Collection /></el-icon>
           <span>知识库构建</span>
         </el-menu-item>

         <el-menu-item index="/rag-chat">
           <el-icon><Connection /></el-icon>
           <span>智能体问答</span>
         </el-menu-item>

        <el-sub-menu index="/exam" class="sidebar-sub-menu">
          <template #title>
            <el-icon><Tickets /></el-icon>
            <span>章节考核</span>
          </template>

          <el-menu-item index="/exam/route">
            <span>学习路线</span>
          </el-menu-item>

          <el-menu-item index="/exam/chapters">
            <span>章节管理</span>
          </el-menu-item>

          <el-menu-item index="/exam/configs">
            <span>考核配置</span>
          </el-menu-item>

          <el-menu-item index="/exam/start">
            <span>开始考核</span>
          </el-menu-item>

          <el-menu-item index="/exam/records">
            <span>考试记录</span>
          </el-menu-item>
        </el-sub-menu>


        <el-menu-item index="/system-logs">
          <el-icon><Document /></el-icon>
          <span>系统日志</span>
        </el-menu-item>

        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>个人中心</span>
        </el-menu-item>

      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div>
          <div style="font-size: 18px; font-weight: 760; color: #fff;">
            人工智能导论课程智能体系统
          </div>
          <div style="font-size: 13px; color: #8793b5; margin-top: 3px;">
            当前阶段：课程资料上传与解析
          </div>
        </div>

        <el-dropdown @command="handleCommand">
          <div style="display: flex; align-items: center; cursor: pointer;">
            <el-avatar
              :size="36"
              style="background: linear-gradient(135deg, #6f8cff, #8e63ff);"
            >
              {{ avatarText }}
            </el-avatar>

            <div style="margin-left: 10px;">
              <div style="color: #fff; font-weight: 650;">
                {{ userInfo.nickname || userInfo.username || "用户" }}
              </div>

              <div style="color: #8995b6; font-size: 12px;">
                {{ roleText }}
              </div>
            </div>
          </div>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                个人中心
              </el-dropdown-item>

              <el-dropdown-item divided command="logout">
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  House,
  User,
  ChatDotRound,
  FolderOpened,
  Tickets,
  Setting,
  Cpu,
  Document,
  Collection,
  Connection
} from "@element-plus/icons-vue"
import { getCurrentUserApi } from "../api/auth"

const route = useRoute()
const router = useRouter()

const userInfo = ref({})

const activeMenu = computed(() => route.path)

const avatarText = computed(() => {
  const name = userInfo.value.nickname || userInfo.value.username || "U"
  return name.slice(0, 1).toUpperCase()
})

const roleText = computed(() => {
  const role = userInfo.value.role

  if (role === "admin") {
    return "管理员"
  }

  if (role === "teacher") {
    return "教师"
  }

  return "学生"
})

onMounted(async () => {
  await loadUserInfo()
})

async function loadUserInfo() {
  const localUser = localStorage.getItem("user_info")

  if (localUser) {
    userInfo.value = JSON.parse(localUser)
  }

  const res = await getCurrentUserApi()

  userInfo.value = res.data
  localStorage.setItem("user_info", JSON.stringify(res.data))
}

function handleCommand(command) {
  if (command === "profile") {
    router.push("/profile")
  }

  if (command === "logout") {
    logout()
  }
}

async function logout() {
  await ElMessageBox.confirm(
    "确定要退出当前账号吗？",
    "退出登录",
    {
      type: "warning",
      confirmButtonText: "退出",
      cancelButtonText: "取消"
    }
  )

  localStorage.removeItem("access_token")
  localStorage.removeItem("user_info")

  ElMessage.success("已退出登录")
  router.push("/login")
}
</script>