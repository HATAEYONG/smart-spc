"""
LLM Service for SPC AI Chatbot
Supports OpenAI and Anthropic Claude API integrations
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """LLM Provider Options"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEMO = "demo"  # Fallback mode without external API


@dataclass
class LLMMessage:
    """Chat Message Structure"""
    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: Optional[datetime] = None


@dataclass
class LLMResponse:
    """LLM Response Structure"""
    content: str
    provider: LLMProvider
    model: str
    tokens_used: int = 0
    cost_estimate: float = 0.0
    cached: bool = False
    error: Optional[str] = None


class PromptTemplates:
    """SPC Chatbot Prompt Templates"""

    SYSTEM_PROMPT = """You are an expert Statistical Process Control (SPC) Quality Management Assistant.
You help manufacturing quality engineers, operators, and managers analyze process data, identify quality issues, and recommend improvements.

Your expertise includes:
- Statistical Process Control (SPC) methodology
- Control charts (X-bar R, CUSUM, EWMA)
- Process capability analysis (Cp, Cpk, Pp, Ppk)
- Run Rules and Western Electric rules
- Quality improvement methodologies (Six Sigma, Kaizen, PDCA)
- Manufacturing quality management best practices

Always provide:
1. Clear, data-driven analysis
2. Actionable recommendations
3. Technical accuracy
4. Professional tone

When analyzing data:
- Interpret statistical indices correctly
- Highlight trends and patterns
- Identify potential risks
- Suggest specific improvement actions

Response in the same language as the user's question (Korean or English).
"""

    CAPABILITY_ANALYSIS_TEMPLATE = """Analyze the following process capability data:

**Product:** {product_name}
**Process Capability Indices:**
- Cp (Potential Capability): {cp:.3f}
- Cpk (Actual Capability): {cpk:.3f}
- Upper Specification Limit (USL): {usl:.4f}
- Lower Specification Limit (LSL): {lsl:.4f}
- Target Value: {target:.4f}
- Process Mean: {mean:.4f}
- Standard Deviation: {std_dev:.4f}

**Additional Data:**
- Sample Size: {sample_size}
- Data Distribution: {is_normal}
- Out of Spec Rate: {oos_rate:.2%}

User Question: {user_message}

Provide a comprehensive analysis including:
1. Process capability assessment (Excellent/Good/Acceptable/Inadequate)
2. Key observations from the indices
3. Potential risks or concerns
4. Specific recommendations for improvement
"""

    TROUBLESHOOTING_TEMPLATE = """Analyze the following quality issues:

**Product:** {product_name}
**Recent Alerts (Last 7 Days):** {alert_count}
**Recent Run Rule Violations:** {violation_count}

**Alert Details:**
{alert_details}

**Violation Details:**
{violation_details}

User Question: {user_message}

Provide:
1. Root cause analysis (consider 4M1E: Man, Machine, Material, Method, Environment)
2. Severity assessment
3. Immediate containment actions
4. Long-term corrective actions
5. Prevention strategies
"""

    TREND_ANALYSIS_TEMPLATE = """Analyze the following trend data:

**Product:** {product_name}
**Analysis Period:** Last 30 days
**Data Points:** {data_count}

**Statistics:**
- Mean: {mean:.4f}
- Standard Deviation: {std_dev:.4f}
- Min: {min_val:.4f}
- Max: {max_val:.4f}
- Coefficient of Variation: {cv:.2f}%

**Trend Analysis:**
- Trend Direction: {trend}
- Slope: {slope:.6f}
- Trend Description: {trend_desc}

User Question: {user_message}

Provide:
1. Trend interpretation
2. Potential impact on quality
3. Predictive insights (next 7-10 days)
4. Monitoring recommendations
5. Early warning indicators to watch
"""

    ROOT_CAUSE_TEMPLATE = """Perform root cause analysis:

**Product:** {product_name}
**Recent Quality Issues:** {alert_count} incidents

**Issue Patterns:**
{issue_patterns}

User Question: {user_message}

Apply 4M1E framework:
1. **Man (Human Factors):** Operator training, fatigue, SOP compliance
2. **Machine (Equipment):** Equipment age, calibration, tool wear
3. **Material:** Raw material quality, lot variations, storage
4. **Method:** Process parameters, cycle time, inspection methods
5. **Environment:** Temperature, humidity, cleanliness

Provide:
- Most likely root causes (ranked by probability)
- Data-driven evidence for each cause
- Verification methods
- Corrective actions
"""

    IMPROVEMENT_TEMPLATE = """Generate improvement recommendations:

**Current State:**
- Product: {product_name}
- Current Cpk: {current_cpk:.3f}
- Target Cpk: {target_cpk:.3f}
- Gap: {cpk_gap:.3f}

**Performance Metrics:**
- Current Defect Rate: {current_ppm:.0f} PPM
- Target Defect Rate: {target_ppm:.0f} PPM

User Question: {user_message}

Provide a phased improvement plan:
1. **Phase 1 - Quick Wins (0-1 month):** Immediate actions
2. **Phase 2 - Process Stabilization (1-3 months):** Medium-term improvements
3. **Phase 3 - Breakthrough (3-6 months):** Long-term transformation

For each phase include:
- Specific actions
- Expected outcomes
- Resource requirements
- Timeline
- Success metrics
"""

    GENERAL_QUERY_TEMPLATE = """User Question: {user_message}

Context: SPC Quality Management System

Provide helpful guidance on statistical process control, quality management, or process improvement.
If the question requires specific product data, ask the user to select a product first."""


class LLMService:
    """
    Main LLM Service with provider switching
    Supports OpenAI GPT and Anthropic Claude
    """

    def __init__(self):
        self.provider = self._get_provider()
        self.api_key = self._get_api_key()
        self.model = self._get_model()
        self.cache_timeout = 3600  # 1 hour

    def _get_provider(self) -> LLMProvider:
        """Determine LLM provider from settings"""
        provider_name = getattr(settings, 'LLM_PROVIDER', 'demo')
        try:
            return LLMProvider(provider_name.lower())
        except ValueError:
            logger.warning(f"Invalid LLM provider: {provider_name}, using DEMO mode")
            return LLMProvider.DEMO

    def _get_api_key(self) -> Optional[str]:
        """Get API key from settings"""
        if self.provider == LLMProvider.OPENAI:
            return os.environ.get('OPENAI_API_KEY', getattr(settings, 'OPENAI_API_KEY', ''))
        elif self.provider == LLMProvider.ANTHROPIC:
            return os.environ.get('ANTHROPIC_API_KEY', getattr(settings, 'ANTHROPIC_API_KEY', ''))
        return None

    def _get_model(self) -> str:
        """Get model name based on provider"""
        if self.provider == LLMProvider.OPENAI:
            return getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        elif self.provider == LLMProvider.ANTHROPIC:
            return getattr(settings, 'ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        return 'demo-model'

    def generate_response(
        self,
        messages: List[LLMMessage],
        use_cache: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """
        Generate LLM response

        Args:
            messages: List of conversation messages
            use_cache: Whether to use cached responses
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with generated content
        """
        # Check cache
        if use_cache and self.provider != LLMProvider.DEMO:
            cache_key = self._generate_cache_key(messages)
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.info(f"Using cached LLM response for key: {cache_key[:20]}...")
                return LLMResponse(**cached_response, cached=True)

        # Generate response based on provider
        try:
            if self.provider == LLMProvider.OPENAI:
                response = self._call_openai(messages, temperature, max_tokens)
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self._call_anthropic(messages, temperature, max_tokens)
            else:
                response = self._demo_response(messages)

            # Cache successful responses
            if use_cache and self.provider != LLMProvider.DEMO and not response.error:
                cache_key = self._generate_cache_key(messages)
                cache.set(cache_key, {
                    'content': response.content,
                    'provider': response.provider.value,
                    'model': response.model,
                    'tokens_used': response.tokens_used,
                    'cost_estimate': response.cost_estimate,
                }, self.cache_timeout)

            return response

        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            return LLMResponse(
                content="I apologize, but I'm having trouble connecting to my AI service. Please try again later.",
                provider=self.provider,
                model=self.model,
                error=str(e)
            )

    def _call_openai(
        self,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Call OpenAI API"""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            content = data['choices'][0]['message']['content']
            tokens_used = data.get('usage', {}).get('total_tokens', 0)

            # Estimate cost (as of 2024)
            # GPT-4o-mini: $0.15/1M input, $0.60/1M output
            cost_estimate = (tokens_used / 1_000_000) * 0.5  # Average estimate

            return LLMResponse(
                content=content,
                provider=LLMProvider.OPENAI,
                model=self.model,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    def _call_anthropic(
        self,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Call Anthropic Claude API"""
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        # Extract system message if present
        system_message = ""
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                chat_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        payload = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_message:
            payload["system"] = system_message

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            content = data['content'][0]['text']
            tokens_used = data.get('usage', {}).get('input_tokens', 0) + data.get('usage', {}).get('output_tokens', 0)

            # Estimate cost (Claude 3.5 Sonnet: $3/1M input, $15/1M output)
            cost_estimate = (tokens_used / 1_000_000) * 9  # Average estimate

            return LLMResponse(
                content=content,
                provider=LLMProvider.ANTHROPIC,
                model=self.model,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

    def _demo_response(self, messages: List[LLMMessage]) -> LLMResponse:
        """Generate demo response without external API"""
        last_message = messages[-1].content if messages else ""

        # Simple keyword-based demo responses
        if "cpk" in last_message.lower() or "capability" in last_message.lower():
            demo_response = """## Demo Mode: Process Capability Analysis

This is a demo response. To enable full AI capabilities, please configure your LLM API key.

### Current Configuration Needed:
- **OpenAI**: Set `OPENAI_API_KEY` environment variable
- **Anthropic**: Set `ANTHROPIC_API_KEY` environment variable

### How to Configure:
1. OpenAI: Get API key from https://platform.openai.com/api-keys
2. Anthropic: Get API key from https://console.anthropic.com/

### Configuration Options:
```python
# In settings.py or .env
LLM_PROVIDER = 'openai'  # or 'anthropic'
OPENAI_API_KEY = 'sk-...'
ANTHROPIC_API_KEY = 'sk-ant-...'
```

### Demo Analysis:
Without actual API access, I can explain how to interpret Cpk:
- **Cpk ≥ 2.0**: Excellent (6σ level)
- **Cpk ≥ 1.67**: Good (5σ level)
- **Cpk ≥ 1.33**: Capable (4σ level)
- **Cpk ≥ 1.0**: Minimum acceptable
- **Cpk < 1.0**: Needs improvement

Configure your API key for detailed, AI-powered analysis!
"""
        elif "trend" in last_message.lower() or "추세" in last_message:
            demo_response = """## Demo Mode: Trend Analysis

This is a demo response. Configure your LLM API key for full AI-powered trend analysis.

### AI-Enhanced Trend Analysis Includes:
1. **Pattern Recognition**: Identify cycles, shifts, trends
2. **Predictive Insights**: Forecast future process behavior
3. **Anomaly Detection**: Spot unusual patterns early
4. **Correlation Analysis**: Link trends to process changes
5. **Actionable Recommendations**: Specific improvement steps

### Setup Instructions:
```bash
# Set your API key
export OPENAI_API_KEY='sk-...'
# or
export ANTHROPIC_API_KEY='sk-ant-...'
```

Then restart your Django server.
"""
        else:
            demo_response = """## SPC AI Assistant - Demo Mode

Hello! I'm the SPC Quality Management AI Assistant.

### ⚠️ Limited Functionality
Currently running in **demo mode** without LLM API integration.

### 🚀 Enable Full AI Capabilities:
Configure your preferred LLM provider:

**Option 1: OpenAI (GPT-4o, GPT-4o-mini)**
```bash
export OPENAI_API_KEY='sk-...'
export LLM_PROVIDER='openai'
```

**Option 2: Anthropic (Claude 3.5 Sonnet)**
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
export LLM_PROVIDER='anthropic'
```

### 📊 What I Can Do with Full AI:
- **Process Capability Analysis**: Deep dive into Cp, Cpk indices
- **Troubleshooting**: Root cause analysis using 4M1E framework
- **Trend Analysis**: Predictive insights and pattern recognition
- **Improvement Recommendations**: Phased improvement plans
- **Real-time Assistance**: Context-aware quality guidance

### 💬 Try asking:
- "Analyze the process capability for this product"
- "Why are we seeing increased defects?"
- "What's the trend for product X?"
- "How can we improve our Cpk?"

Configure your API key now for intelligent, AI-powered quality management!
"""

        return LLMResponse(
            content=demo_response,
            provider=LLMProvider.DEMO,
            model='demo-model',
            tokens_used=0,
            cost_estimate=0.0
        )

    def _generate_cache_key(self, messages: List[LLMMessage]) -> str:
        """Generate cache key from messages"""
        import hashlib
        message_str = json.dumps([{"role": m.role, "content": m.content} for m in messages])
        return hashlib.md5(message_str.encode()).hexdigest()

    def build_messages(
        self,
        template: str,
        context: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> List[LLMMessage]:
        """
        Build message list from template and context

        Args:
            template: Prompt template string
            context: Variables to substitute in template
            conversation_history: Optional conversation history

        Returns:
            List of LLMMessage objects
        """
        messages = []

        # System prompt
        messages.append(LLMMessage(
            role="system",
            content=PromptTemplates.SYSTEM_PROMPT
        ))

        # Add conversation history
        if conversation_history:
            for hist_msg in conversation_history[-10:]:  # Last 10 messages
                messages.append(LLMMessage(
                    role=hist_msg.get("role", "user"),
                    content=hist_msg.get("content", "")
                ))

        # Current user message with template
        user_content = template.format(**context)
        messages.append(LLMMessage(
            role="user",
            content=user_content
        ))

        return messages


class SPCChatbotService:
    """
    High-level SPC Chatbot Service
    Integrates with existing SPC chatbot logic
    """

    def __init__(self):
        self.llm_service = LLMService()

    def chat(
        self,
        user_message: str,
        intent: str,
        context_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate chatbot response

        Args:
            user_message: User's question
            intent: Detected intent (capability_analysis, troubleshooting, etc.)
            context_data: SPC data context (product info, statistics, etc.)
            conversation_history: Optional conversation history

        Returns:
            Response dict with content and metadata
        """
        # Select template based on intent
        template_map = {
            'capability_analysis': PromptTemplates.CAPABILITY_ANALYSIS_TEMPLATE,
            'troubleshooting': PromptTemplates.TROUBLESHOOTING_TEMPLATE,
            'trend_analysis': PromptTemplates.TREND_ANALYSIS_TEMPLATE,
            'root_cause': PromptTemplates.ROOT_CAUSE_TEMPLATE,
            'improvement': PromptTemplates.IMPROVEMENT_TEMPLATE,
            'general': PromptTemplates.GENERAL_QUERY_TEMPLATE,
        }

        template = template_map.get(intent, PromptTemplates.GENERAL_QUERY_TEMPLATE)

        # Prepare context
        context = {
            'user_message': user_message,
            **context_data
        }

        # Build messages
        messages = self.llm_service.build_messages(
            template=template,
            context=context,
            conversation_history=conversation_history
        )

        # Generate response
        llm_response = self.llm_service.generate_response(messages)

        return {
            'response': llm_response.content,
            'provider': llm_response.provider.value,
            'model': llm_response.model,
            'tokens_used': llm_response.tokens_used,
            'cost_estimate': llm_response.cost_estimate,
            'cached': llm_response.cached,
            'error': llm_response.error,
        }

    def get_provider_status(self) -> Dict[str, Any]:
        """Get current LLM provider status"""
        return {
            'provider': self.llm_service.provider.value,
            'model': self.llm_service.model,
            'configured': bool(self.llm_service.api_key) or self.llm_service.provider == LLMProvider.DEMO,
            'api_key_set': bool(self.llm_service.api_key),
        }


# Singleton instance
_spc_chatbot_service = None

def get_spc_chatbot_service() -> SPCChatbotService:
    """Get singleton SPC chatbot service instance"""
    global _spc_chatbot_service
    if _spc_chatbot_service is None:
        _spc_chatbot_service = SPCChatbotService()
    return _spc_chatbot_service
