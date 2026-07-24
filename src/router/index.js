import { createRouter, createWebHistory } from "vue-router"

import Login from "../views/Login.vue"
import Register from "../views/Register.vue"
import Layout from "../views/Layout.vue"
import Home from "../views/Home.vue"
import UserCenter from "../views/UserCenter.vue"
import ModelConfig from "../views/ModelConfig.vue"
import AgentManage from "../views/AgentManage.vue"
import ChatHistory from "../views/ChatHistory.vue"
import SystemLog from "../views/SystemLog.vue"
import Materials from "../views/Materials.vue"
import KnowledgeBase from "../views/KnowledgeBase.vue"
import RagChat from "../views/RagChat.vue"

import ChapterManage from "../views/exam/ChapterManage.vue"
import ExamConfigManage from "../views/exam/ExamConfigManage.vue"
import ChapterRoute from "../views/exam/ChapterRoute.vue"
import ExamStart from "../views/exam/ExamStart.vue"
import ExamDo from "../views/exam/ExamDo.vue"
import ExamRecords from "../views/exam/ExamRecords.vue"
import ExamReport from "../views/exam/ExamReport.vue"


const routes = [
  {
    path: "/",
    redirect: "/home"
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: {
      public: true
    }
  },
  {
    path: "/register",
    name: "Register",
    component: Register,
    meta: {
      public: true
    }
  },
  {
    path: "/",
    component: Layout,
    children: [
      {
        path: "home",
        name: "Home",
        component: Home
      },
      {
        path: "profile",
        name: "UserCenter",
        component: UserCenter
      },
      {
        path: "model-config",
        name: "ModelConfig",
        component: ModelConfig
      },
      {
        path: "agents",
        name: "AgentManage",
        component: AgentManage
      },
      {
        path: "materials",
        name: "Materials",
        component: Materials
      },
      {
        path: "knowledge-base",
        name: "KnowledgeBase",
        component: KnowledgeBase
      },
      {
        path: "rag-chat",
        name: "RagChat",
        component: RagChat
      },
      {
        path: "chat-history",
        name: "ChatHistory",
        component: ChatHistory
      },
      {
        path: "system-logs",
        name: "SystemLog",
        component: SystemLog
      },

      // =========================
      // 章节考核模块
      // =========================
      {
        path: "exam/route",
        name: "ChapterRoute",
        component: ChapterRoute
      },
      {
        path: "exam/chapters",
        name: "ChapterManage",
        component: ChapterManage
      },
      {
        path: "exam/configs",
        name: "ExamConfigManage",
        component: ExamConfigManage
      },
      {
        path: "exam/start",
        name: "ExamStart",
        component: ExamStart
      },
      {
        path: "exam/do/:examId",
        name: "ExamDo",
        component: ExamDo
      },
      {
        path: "exam/records",
        name: "ExamRecords",
        component: ExamRecords
      },
      {
        path: "exam/report/:examId",
        name: "ExamReport",
        component: ExamReport
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("access_token")

  if (to.meta.public) {
    if (token && (to.path === "/login" || to.path === "/register")) {
      next("/home")
    } else {
      next()
    }

    return
  }

  if (!token) {
    next("/login")
  } else {
    next()
  }
})

export default router
