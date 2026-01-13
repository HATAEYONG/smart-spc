"""
AI Service Integration
Supports OpenAI GPT, Anthropic Claude, Google Gemini, and Open Source Models
"""
import os
from typing import Dict, List, Optional
import httpx
from django.conf import settings


class AIServiceBase:
    """Base class for AI services"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class OpenAIService(AIServiceBase):
    """OpenAI GPT Service"""

    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        super().__init__(api_key)
        self.base_url = "https://api.openai.com/v1"

    async def classify_qcost(
        self,
        description: str,
        amount: int,
        context: str = ""
    ) -> Dict:
        """
        Classify Q-COST using GPT-4

        Returns:
            Dict with suggested_category, suggested_item, confidence, reasoning
        """
        prompt = f"""
You are a quality cost classification expert. Classify the following cost entry:

Description: {description}
Amount: {amount}
Context: {context}

Available categories:
- PREVENTION: Prevention costs (training, planning, quality engineering)
- APPRAISAL: Appraisal costs (inspection, testing, auditing)
- INTERNAL_FAILURE: Internal failure costs (scrap, rework, re-inspection)
- EXTERNAL_FAILURE: External failure costs (warranty, complaints, returns)

Provide your response in the following JSON format:
{{
    "suggested_category": "PREVENTION|APPRAISAL|INTERNAL_FAILURE|EXTERNAL_FAILURE",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation"
}}
"""

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are a quality cost classification expert."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']

            import json
            return json.loads(content)

        except Exception as e:
            return {
                "suggested_category": "",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}"
            }

    async def analyze_root_cause(
        self,
        problem_description: str,
        defect_details: str,
        context: str = ""
    ) -> Dict:
        """
        Analyze root cause using GPT-4

        Returns:
            Dict with root_cause, confidence, recommended_actions
        """
        prompt = f"""
You are a quality engineering expert specializing in root cause analysis.

Problem: {problem_description}
Defect Details: {defect_details}
Context: {context}

Analyze the root cause and provide recommendations in the following JSON format:
{{
    "root_cause": "Primary root cause",
    "confidence": 0.0-1.0,
    "recommended_corrective_actions": ["action 1", "action 2"],
    "recommended_preventive_actions": ["action 1", "action 2"],
    "reasoning": "Detailed analysis"
}}
"""

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are a quality engineering expert."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']

            import json
            return json.loads(content)

        except Exception as e:
            return {
                "root_cause": "",
                "confidence": 0.0,
                "recommended_corrective_actions": [],
                "recommended_preventive_actions": [],
                "reasoning": f"Error: {str(e)}"
            }


class AnthropicService(AIServiceBase):
    """Anthropic Claude Service"""

    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("Anthropic API key not provided")
        super().__init__(api_key)
        self.base_url = "https://api.anthropic.com/v1"

    async def classify_qcost(
        self,
        description: str,
        amount: int,
        context: str = ""
    ) -> Dict:
        """
        Classify Q-COST using Claude

        Returns:
            Dict with suggested_category, suggested_item, confidence, reasoning
        """
        prompt = f"""
You are a quality cost classification expert. Classify the following cost entry:

Description: {description}
Amount: {amount}
Context: {context}

Available categories:
- PREVENTION: Prevention costs (training, planning, quality engineering)
- APPRAISAL: Appraisal costs (inspection, testing, auditing)
- INTERNAL_FAILURE: Internal failure costs (scrap, rework, re-inspection)
- EXTERNAL_FAILURE: External failure costs (warranty, complaints, returns)

Provide your response in the following JSON format:
{{
    "suggested_category": "PREVENTION|APPRAISAL|INTERNAL_FAILURE|EXTERNAL_FAILURE",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation"
}}
"""

        try:
            response = await self.client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 1024,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            response.raise_for_status()
            result = response.json()
            content = result['content'][0]['text']

            import json
            return json.loads(content)

        except Exception as e:
            return {
                "suggested_category": "",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}"
            }

    async def analyze_root_cause(
        self,
        problem_description: str,
        defect_details: str,
        context: str = ""
    ) -> Dict:
        """
        Analyze root cause using Claude

        Returns:
            Dict with root_cause, confidence, recommended_actions
        """
        prompt = f"""
You are a quality engineering expert specializing in root cause analysis.

Problem: {problem_description}
Defect Details: {defect_details}
Context: {context}

Analyze the root cause and provide recommendations in the following JSON format:
{{
    "root_cause": "Primary root cause",
    "confidence": 0.0-1.0,
    "recommended_corrective_actions": ["action 1", "action 2"],
    "recommended_preventive_actions": ["action 1", "action 2"],
    "reasoning": "Detailed analysis"
}}
"""

        try:
            response = await self.client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 2048,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            response.raise_for_status()
            result = response.json()
            content = result['content'][0]['text']

            import json
            return json.loads(content)

        except Exception as e:
            return {
                "root_cause": "",
                "confidence": 0.0,
                "recommended_corrective_actions": [],
                "recommended_preventive_actions": [],
                "reasoning": f"Error: {str(e)}"
            }


class GeminiService(AIServiceBase):
    """Google Gemini Service"""

    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Gemini API key not provided")
        super().__init__(api_key)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def classify_qcost(
        self,
        description: str,
        amount: int,
        context: str = ""
    ) -> Dict:
        """
        Classify Q-COST using Gemini

        Returns:
            Dict with suggested_category, suggested_item, confidence, reasoning
        """
        prompt = f"""
You are a quality cost classification expert. Classify the following cost entry:

Description: {description}
Amount: {amount}
Context: {context}

Available categories:
- PREVENTION: Prevention costs (training, planning, quality engineering)
- APPRAISAL: Appraisal costs (inspection, testing, auditing)
- INTERNAL_FAILURE: Internal failure costs (scrap, rework, re-inspection)
- EXTERNAL_FAILURE: External failure costs (warranty, complaints, returns)

Provide your response in the following JSON format:
{{
    "suggested_category": "PREVENTION|APPRAISAL|INTERNAL_FAILURE|EXTERNAL_FAILURE",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation"
}}
"""

        try:
            response = await self.client.post(
                f"{self.base_url}/models/gemini-pro:generateContent?key={self.api_key}",
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 1024
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']

            # Extract JSON from markdown code blocks if present
            import json
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)

            return json.loads(content)

        except Exception as e:
            return {
                "suggested_category": "",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}"
            }

    async def analyze_root_cause(
        self,
        problem_description: str,
        defect_details: str,
        context: str = ""
    ) -> Dict:
        """
        Analyze root cause using Gemini

        Returns:
            Dict with root_cause, confidence, recommended_actions
        """
        prompt = f"""
You are a quality engineering expert specializing in root cause analysis.

Problem: {problem_description}
Defect Details: {defect_details}
Context: {context}

Analyze the root cause and provide recommendations in the following JSON format:
{{
    "root_cause": "Primary root cause",
    "confidence": 0.0-1.0,
    "recommended_corrective_actions": ["action 1", "action 2"],
    "recommended_preventive_actions": ["action 1", "action 2"],
    "reasoning": "Detailed analysis"
}}
"""

        try:
            response = await self.client.post(
                f"{self.base_url}/models/gemini-pro:generateContent?key={self.api_key}",
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 2048
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']

            # Extract JSON from markdown code blocks if present
            import json
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)

            return json.loads(content)

        except Exception as e:
            return {
                "root_cause": "",
                "confidence": 0.0,
                "recommended_corrective_actions": [],
                "recommended_preventive_actions": [],
                "reasoning": f"Error: {str(e)}"
            }


class OpenSourceService(AIServiceBase):
    """
    Open Source Model Service (via Ollama or HuggingFace)
    Supports: Llama, Mistral, CodeLlama, etc.
    """

    def __init__(self, provider: str = "ollama", model: str = "llama2"):
        """
        Args:
            provider: "ollama" or "huggingface"
            model: Model name (e.g., "llama2", "mistral", "codellama")
        """
        self.provider = provider
        self.model = model

        if provider == "ollama":
            base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            self.client = httpx.AsyncClient(timeout=120.0, base_url=base_url)
        elif provider == "huggingface":
            api_key = os.getenv('HUGGINGFACE_API_KEY')
            if not api_key:
                raise ValueError("HuggingFace API key not provided")
            super().__init__(api_key)
            self.base_url = "https://api-inference.huggingface.co"

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def classify_qcost(
        self,
        description: str,
        amount: int,
        context: str = ""
    ) -> Dict:
        """
        Classify Q-COST using Open Source Models

        Returns:
            Dict with suggested_category, suggested_item, confidence, reasoning
        """
        prompt = f"""You are a quality cost classification expert. Classify the following cost entry:

Description: {description}
Amount: {amount}
Context: {context}

Available categories:
- PREVENTION: Prevention costs (training, planning, quality engineering)
- APPRAISAL: Appraisal costs (inspection, testing, auditing)
- INTERNAL_FAILURE: Internal failure costs (scrap, rework, re-inspection)
- EXTERNAL_FAILURE: External failure costs (warranty, complaints, returns)

Respond with only the category name and confidence score in this format:
CATEGORY: [PREVENTION|APPRAISAL|INTERNAL_FAILURE|EXTERNAL_FAILURE]
CONFIDENCE: [0.0-1.0]
REASONING: [brief explanation]"""

        try:
            if self.provider == "ollama":
                response = await self.client.post(
                    "/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 256
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result.get("response", "")

                # Parse response
                import re
                category_match = re.search(r'CATEGORY:\s*(\w+)', content)
                confidence_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', content)
                reasoning_match = re.search(r'REASONING:\s*(.*)', content, re.DOTALL)

                return {
                    "suggested_category": category_match.group(1) if category_match else "",
                    "confidence": float(confidence_match.group(1)) if confidence_match else 0.0,
                    "reasoning": reasoning_match.group(1).strip() if reasoning_match else content
                }

            elif self.provider == "huggingface":
                response = await self.client.post(
                    f"/models/{self.model}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "temperature": 0.3,
                            "max_new_tokens": 256,
                            "return_full_text": False
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result[0].get("generated_text", "") if isinstance(result, list) else ""

                # Parse response
                import re
                category_match = re.search(r'CATEGORY:\s*(\w+)', content)
                confidence_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', content)
                reasoning_match = re.search(r'REASONING:\s*(.*)', content, re.DOTALL)

                return {
                    "suggested_category": category_match.group(1) if category_match else "",
                    "confidence": float(confidence_match.group(1)) if confidence_match else 0.0,
                    "reasoning": reasoning_match.group(1).strip() if reasoning_match else content
                }

        except Exception as e:
            return {
                "suggested_category": "",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}"
            }

    async def analyze_root_cause(
        self,
        problem_description: str,
        defect_details: str,
        context: str = ""
    ) -> Dict:
        """
        Analyze root cause using Open Source Models

        Returns:
            Dict with root_cause, confidence, recommended_actions
        """
        prompt = f"""You are a quality engineering expert specializing in root cause analysis.

Problem: {problem_description}
Defect Details: {defect_details}
Context: {context}

Provide:
ROOT_CAUSE: [primary root cause]
CONFIDENCE: [0.0-1.0]
CORRECTIVE_ACTIONS: [action 1, action 2]
PREVENTIVE_ACTIONS: [action 1, action 2]
REASONING: [detailed analysis]"""

        try:
            if self.provider == "ollama":
                response = await self.client.post(
                    "/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 512
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result.get("response", "")

                # Parse response
                import re
                root_cause_match = re.search(r'ROOT_CAUSE:\s*(.*)', content)
                confidence_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', content)
                corrective_match = re.search(r'CORRECTIVE_ACTIONS:\s*(.*)', content)
                preventive_match = re.search(r'PREVENTIVE_ACTIONS:\s*(.*)', content)
                reasoning_match = re.search(r'REASONING:\s*(.*)', content, re.DOTALL)

                return {
                    "root_cause": root_cause_match.group(1).strip() if root_cause_match else "",
                    "confidence": float(confidence_match.group(1)) if confidence_match else 0.0,
                    "recommended_corrective_actions": [action.strip() for action in corrective_match.group(1).split(",")] if corrective_match else [],
                    "recommended_preventive_actions": [action.strip() for action in preventive_match.group(1).split(",")] if preventive_match else [],
                    "reasoning": reasoning_match.group(1).strip() if reasoning_match else content
                }

            elif self.provider == "huggingface":
                response = await self.client.post(
                    f"/models/{self.model}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "temperature": 0.3,
                            "max_new_tokens": 512,
                            "return_full_text": False
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result[0].get("generated_text", "") if isinstance(result, list) else ""

                # Parse response
                import re
                root_cause_match = re.search(r'ROOT_CAUSE:\s*(.*)', content)
                confidence_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', content)
                corrective_match = re.search(r'CORRECTIVE_ACTIONS:\s*(.*)', content)
                preventive_match = re.search(r'PREVENTIVE_ACTIONS:\s*(.*)', content)
                reasoning_match = re.search(r'REASONING:\s*(.*)', content, re.DOTALL)

                return {
                    "root_cause": root_cause_match.group(1).strip() if root_cause_match else "",
                    "confidence": float(confidence_match.group(1)) if confidence_match else 0.0,
                    "recommended_corrective_actions": [action.strip() for action in corrective_match.group(1).split(",")] if corrective_match else [],
                    "recommended_preventive_actions": [action.strip() for action in preventive_match.group(1).split(",")] if preventive_match else [],
                    "reasoning": reasoning_match.group(1).strip() if reasoning_match else content
                }

        except Exception as e:
            return {
                "root_cause": "",
                "confidence": 0.0,
                "recommended_corrective_actions": [],
                "recommended_preventive_actions": [],
                "reasoning": f"Error: {str(e)}"
            }


def get_ai_service():
    """
    Factory function to get AI service based on configuration

    Environment Variables:
    - AI_PROVIDER: openai, anthropic, gemini, ollama, huggingface
    - OPENAI_API_KEY: OpenAI API key
    - ANTHROPIC_API_KEY: Anthropic API key
    - GEMINI_API_KEY: Google Gemini API key
    - HUGGINGFACE_API_KEY: HuggingFace API key
    - OLLAMA_BASE_URL: Ollama server URL (default: http://localhost:11434)
    - OPEN_SOURCE_MODEL: Model name for open source (default: llama2, mistral, codellama)
    """
    provider = os.getenv('AI_PROVIDER', 'openai').lower()

    if provider == 'openai':
        return OpenAIService()
    elif provider == 'anthropic':
        return AnthropicService()
    elif provider == 'gemini':
        return GeminiService()
    elif provider == 'ollama':
        model = os.getenv('OPEN_SOURCE_MODEL', 'llama2')
        return OpenSourceService(provider='ollama', model=model)
    elif provider == 'huggingface':
        model = os.getenv('OPEN_SOURCE_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2')
        return OpenSourceService(provider='huggingface', model=model)
    else:
        raise ValueError(f"Unsupported AI provider: {provider}. Supported: openai, anthropic, gemini, ollama, huggingface")
