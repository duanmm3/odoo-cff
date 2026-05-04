# -*- coding: utf-8 -*-
"""LLM Service — llama-server API 封装"""

import requests
import json
import logging

_logger = logging.getLogger(__name__)


class LLMService:
    """llama-server API 调用封装"""

    def __init__(self, api_base=None, model='local-model', timeout=120):
        self.api_base = api_base or 'https://genuine-applicants-templates-differ.trycloudflare.com/v1'
        self.model = model
        self.timeout = timeout

    def chat(self, messages, temperature=0, max_tokens=4096, response_format=None):
        """调用 Chat Completions API"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if response_format:
            payload["response_format"] = response_format

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            _logger.error("LLM API 请求超时")
            raise Exception("LLM 服务响应超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            _logger.error("LLM API 连接失败")
            raise Exception("无法连接 LLM 服务，请检查网络配置")
        except Exception as e:
            _logger.error(f"LLM API 调用失败: {e}")
            raise Exception(f"LLM 服务调用失败: {str(e)}")

    def chat_json(self, messages, temperature=0, max_tokens=4096):
        """调用 LLM 并解析 JSON 响应"""
        text = self.chat(
            messages, temperature, max_tokens,
            response_format={"type": "json_object"}
        )
        return json.loads(text)