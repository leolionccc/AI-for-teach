import json
from typing import AsyncGenerator, Dict, List, Optional

import httpx

from app.models.model_config import ModelConfig


def build_chat_completion_url(api_base_url: str) -> str:
    """
    构建 OpenAI 兼容 chat completions 地址

    支持：
    1. https://api.deepseek.com
    2. https://api.deepseek.com/v1
    3. https://api.xxx.com/v1/chat/completions
    """
    base = api_base_url.rstrip("/")

    if base.endswith("/chat/completions"):
        return base

    if base.endswith("/v1"):
        return f"{base}/chat/completions"

    return f"{base}/v1/chat/completions"


async def stream_openai_compatible_chat(
    model_config: ModelConfig,
    messages: List[Dict[str, str]],
) -> AsyncGenerator[str, None]:
    """
    调用 OpenAI 兼容接口并流式返回文本

    适配：
    - DeepSeek
    - OpenAI
    - Qwen OpenAI Compatible
    - 自定义兼容接口
    """
    if not model_config.api_key:
        raise ValueError("当前大模型配置没有 API Key")

    if not model_config.api_base_url:
        raise ValueError("当前大模型配置没有 API 地址")

    url = build_chat_completion_url(model_config.api_base_url)

    temperature = 0.7

    try:
        temperature = float(model_config.temperature)
    except Exception:
        temperature = 0.7

    payload = {
        "model": model_config.model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": model_config.max_tokens,
        "stream": True,
    }

    headers = {
        "Authorization": f"Bearer {model_config.api_key}",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(
        connect=20.0,
        read=120.0,
        write=120.0,
        pool=20.0,
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream(
            "POST",
            url,
            headers=headers,
            json=payload,
        ) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                raise ValueError(
                    f"大模型接口调用失败，状态码：{response.status_code}，响应：{error_text.decode('utf-8', errors='ignore')}"
                )

            async for line in response.aiter_lines():
                if not line:
                    continue

                if not line.startswith("data:"):
                    continue

                data = line.replace("data:", "", 1).strip()

                if data == "[DONE]":
                    break

                try:
                    event = json.loads(data)
                    choices = event.get("choices", [])

                    if not choices:
                        continue

                    delta = choices[0].get("delta", {})
                    content = delta.get("content")

                    if content:
                        yield content

                except Exception:
                    continue


async def fallback_stream_answer(
    question: str,
    context: str,
    reason: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    当未配置模型或模型调用失败时，返回一个本地兜底答案

    这样你的项目即使没有 API Key，也能完整演示 RAG 流程。
    """
    prefix = "当前未成功调用大模型"

    if reason:
        prefix += f"：{reason}"

    answer = (
        f"{prefix}。\n\n"
        f"下面是系统根据课程知识库检索到的相关资料内容，可作为回答参考：\n\n"
        f"问题：{question}\n\n"
        f"{context}\n\n"
        f"建议：请检查大模型配置页面中的 API Key、API 地址和模型名称，然后重新提问。"
    )

    for char in answer:
        yield char



async def chat_completion_once(
    model_config: ModelConfig,
    messages: List[Dict[str, str]],
) -> str:
    """
    非流式调用 OpenAI 兼容 chat completions 接口

    用途：
    1. 生成章节考核题目
    2. 生成学习评价报告
    """

    if not model_config.api_key:
        raise ValueError("当前大模型配置没有 API Key")

    if not model_config.api_base_url:
        raise ValueError("当前大模型配置没有 API 地址")

    url = build_chat_completion_url(model_config.api_base_url)

    try:
        temperature = float(model_config.temperature)
    except Exception:
        temperature = 0.7

    payload = {
        "model": model_config.model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": model_config.max_tokens,
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {model_config.api_key}",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(
        connect=20.0,
        read=120.0,
        write=120.0,
        pool=20.0,
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            url,
            headers=headers,
            json=payload,
        )

    if response.status_code != 200:
        raise ValueError(
            f"大模型接口调用失败，状态码：{response.status_code}，响应：{response.text}"
        )

    data = response.json()
    choices = data.get("choices", [])

    if not choices:
        return ""

    message = choices[0].get("message", {})
    return message.get("content", "") or ""