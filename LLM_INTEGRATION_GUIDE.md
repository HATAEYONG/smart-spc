# LLM API Integration Guide

## Overview

The SPC Quality Management System now includes integrated LLM (Large Language Model) support for intelligent AI chatbot capabilities. The system supports multiple LLM providers:

- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
- **Demo Mode**: Fallback without external API (for testing)

---

## Features

### AI-Powered Chatbot Capabilities

1. **Process Capability Analysis**
   - Deep analysis of Cp, Cpk indices
   - Identifies capability gaps and risks
   - Provides improvement recommendations

2. **Quality Troubleshooting**
   - Root cause analysis using 4M1E framework
   - Pattern recognition in quality issues
   - Corrective and preventive actions

3. **Trend Analysis**
   - Predictive insights from historical data
   - Anomaly and pattern detection
   - Early warning indicators

4. **Root Cause Analysis**
   - Systematic 4M1E investigation
   - Data-driven evidence
   - Verification methods

5. **Improvement Recommendations**
   - Phased improvement plans
   - Resource requirements
   - Success metrics

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the backend directory or set environment variables:

```bash
# LLM Provider Selection
LLM_PROVIDER=openai  # Options: openai, anthropic, demo

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini  # Options: gpt-4o, gpt-4o-mini, gpt-3.5-turbo

# Anthropic Claude Configuration
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Options: claude-3-5-sonnet-20241022, claude-3-opus-20240229
```

### 2. Settings Configuration (config/settings/dev.py)

The LLM configuration is already added to your Django settings:

```python
# LLM (Large Language Model) Service Configuration
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'demo')

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

# Anthropic Claude Configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
ANTHROPIC_MODEL = os.environ.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')

# LLM Cache Settings
LLM_CACHE_TIMEOUT = 3600  # 1 hour
```

---

## Setup Instructions

### Option 1: OpenAI Integration

1. **Get API Key**
   - Visit https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key (starts with `sk-`)

2. **Configure Environment**
   ```bash
   # Windows PowerShell
   $env:LLM_PROVIDER="openai"
   $env:OPENAI_API_KEY="sk-your-key-here"

   # Linux/Mac
   export LLM_PROVIDER=openai
   export OPENAI_API_KEY="sk-your-key-here"
   ```

3. **Restart Django Server**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac

   python manage.py runserver 8000
   ```

### Option 2: Anthropic Claude Integration

1. **Get API Key**
   - Visit https://console.anthropic.com/
   - Navigate to API Keys
   - Create a new API key
   - Copy the key (starts with `sk-ant-`)

2. **Configure Environment**
   ```bash
   # Windows PowerShell
   $env:LLM_PROVIDER="anthropic"
   $env:ANTHROPIC_API_KEY="sk-ant-your-key-here"

   # Linux/Mac
   export LLM_PROVIDER=anthropic
   export ANTHROPIC_API_KEY="sk-ant-your-key-here"
   ```

3. **Restart Django Server**
   ```bash
   python manage.py runserver 8000
   ```

### Option 3: Demo Mode (No API Key Required)

The system defaults to demo mode if no API key is configured:

```bash
# No configuration needed
LLM_PROVIDER=demo  # (default)
```

Demo mode provides:
- Basic keyword-based responses
- Configuration instructions
- Feature explanations
- No external API calls

---

## API Usage

### 1. Check LLM Status

```bash
GET /api/spc/chatbot/status/
```

**Response:**
```json
{
  "status": "online",
  "llm_integration": true,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "configured": true,
  "api_key_set": true,
  "configuration": {
    "openai_available": true,
    "anthropic_available": false,
    "demo_mode": false
  }
}
```

### 2. Get Chatbot Capabilities

```bash
GET /api/spc/chatbot/capabilities/
```

**Response:**
```json
{
  "name": "SPC Quality Control Chatbot",
  "version": "2.0.0",
  "llm_provider": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "configured": true,
    "api_key_set": true
  },
  "capabilities": [
    {
      "intent": "capability_analysis",
      "description": "Process Capability Analysis",
      "examples": [
        "What is the process capability for product 1?",
        "Why is the Cpk low?"
      ]
    },
    ...
  ]
}
```

### 3. Chat with AI

```bash
POST /api/spc/chatbot/chat/
Content-Type: application/json

{
  "message": "Analyze the process capability for product 1",
  "product_id": 1,
  "session_id": "user-session-123"  // Optional, for conversation history
}
```

**Response:**
```json
{
  "response": "## Process Capability Analysis\n\n**Product:** M10 Bolt\n\n**Capability Indices:**\n- Cp: 2.13 (Excellent)\n- Cpk: 1.70 (Good)\n\n**Analysis:**\nThe process demonstrates excellent capability...",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "tokens_used": 847,
  "cost_estimate": 0.0004,
  "cached": false,
  "error": null,
  "intent": "capability_analysis",
  "session_id": "user-session-123"
}
```

---

## Cost Estimation

### OpenAI Pricing (as of 2024)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|-----------------------|
| GPT-4o | $5.00 | $15.00 |
| GPT-4o-mini | $0.15 | $0.60 |
| GPT-3.5-turbo | $0.50 | $1.50 |

**Estimated costs per conversation:**
- GPT-4o-mini: ~$0.0003 - $0.001 per query
- GPT-4o: ~$0.01 - $0.03 per query

### Anthropic Pricing (as of 2024)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|-----------------------|
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| Claude 3 Opus | $15.00 | $75.00 |

**Estimated costs per conversation:**
- Claude 3.5 Sonnet: ~$0.0002 - $0.001 per query
- Claude 3 Opus: ~$0.001 - $0.005 per query

---

## Features Comparison

| Feature | Demo Mode | OpenAI | Anthropic |
|---------|-----------|--------|-----------|
| Basic Responses | ✅ | ✅ | ✅ |
| Context-Aware Analysis | ❌ | ✅ | ✅ |
| Process Capability Insights | ⚠️ Limited | ✅ | ✅ |
| Root Cause Analysis | ⚠️ Limited | ✅ | ✅ |
| Trend Prediction | ❌ | ✅ | ✅ |
| Conversation History | ❌ | ✅ | ✅ |
| Cost | FREE | Paid | Paid |
| Response Quality | Basic | High | Very High |

---

## Prompt Templates

The system uses specialized prompts for each intent:

### 1. Capability Analysis Template
```python
"""
Analyze the following process capability data:

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
1. Process capability assessment
2. Key observations from the indices
3. Potential risks or concerns
4. Specific recommendations for improvement
"""
```

### 2. Troubleshooting Template
```python
"""
Analyze the following quality issues:

**Product:** {product_name}
**Recent Alerts (Last 7 Days):** {alert_count}
**Recent Run Rule Violations:** {violation_count}

**Alert Details:**
{alert_details}

**Violation Details:**
{violation_details}

User Question: {user_message}

Provide:
1. Root cause analysis (consider 4M1E)
2. Severity assessment
3. Immediate containment actions
4. Long-term corrective actions
5. Prevention strategies
"""
```

### 3. Trend Analysis Template
```python
"""
Analyze the following trend data:

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
```

---

## Troubleshooting

### Issue: "OpenAI API key not configured"

**Solution:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
export LLM_PROVIDER="openai"
```

Restart the Django server after setting the environment variable.

### Issue: "Anthropic API key not configured"

**Solution:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export LLM_PROVIDER="anthropic"
```

Restart the Django server after setting the environment variable.

### Issue: High API Costs

**Solutions:**

1. **Use more cost-effective models**
   ```bash
   export OPENAI_MODEL="gpt-4o-mini"  # Cheaper than gpt-4o
   ```

2. **Enable caching** (already enabled by default)
   - Responses are cached for 1 hour
   - Same questions won't incur additional API calls

3. **Use demo mode for testing**
   ```bash
   export LLM_PROVIDER="demo"
   ```

4. **Set spending limits** in your OpenAI/Anthropic console

### Issue: Slow response times

**Possible causes:**
- Network latency to API servers
- Large prompt size (lots of data context)

**Solutions:**
- Reduce context data sent to LLM
- Use faster models (gpt-4o-mini vs gpt-4o)
- Check internet connection

### Issue: Inaccurate responses

**Possible causes:**
- Insufficient context data
- Wrong intent classification

**Solutions:**
- Ensure product_id is provided
- Check data quality in database
- Verify intent detection in logs

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ChatbotPage.tsx                         │  │
│  │  - User message input                                │  │
│  │  - Product selection                                 │  │
│  │  - Response display                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Django)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           ChatbotViewSet (views.py)                  │  │
│  │  1. Receive user message                             │  │
│  │  2. Detect intent (SPCQualityChatbot)               │  │
│  │  3. Prepare context data                             │  │
│  │  4. Call LLM service                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          LLMService (llm_service.py)                 │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  Provider Switching                             │ │  │
│  │  │  - OpenAI GPT                                   │ │  │
│  │  │  - Anthropic Claude                             │ │  │
│  │  │  - Demo Mode (fallback)                         │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │                                                       │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  Prompt Templates                               │ │  │
│  │  │  - Capability Analysis                          │ │  │
│  │  │  - Troubleshooting                              │ │  │
│  │  │  - Trend Analysis                               │ │  │
│  │  │  - Root Cause Analysis                          │ │  │
│  │  │  - Improvement Recommendations                   │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │                                                       │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  Response Caching                               │ │  │
│  │  │  - Cache key: MD5(messages)                     │ │  │
│  │  │  - TTL: 1 hour                                  │ │  │
│  │  │  - Backend: Django cache                        │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            │ HTTP Request                    │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         External LLM API                             │  │
│  │  - OpenAI API: https://api.openai.com/v1            │  │
│  │  - Anthropic API: https://api.anthropic.com/v1      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Database (Optional)                         │
│  - ChatConversation (session tracking)                     │
│  - ChatMessage (conversation history)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### 1. API Key Security

❌ **Don't:**
- Commit API keys to git
- Share API keys publicly
- Hardcode keys in source code

✅ **Do:**
- Use environment variables
- Add `.env` to `.gitignore`
- Rotate keys periodically
- Monitor usage in API console

### 2. Cost Management

✅ **Do:**
- Start with demo mode for testing
- Use cost-effective models (gpt-4o-mini, Claude 3.5 Sonnet)
- Enable caching (default)
- Set monthly budget limits
- Monitor usage regularly

### 3. Prompt Engineering

✅ **Do:**
- Provide specific context data
- Include relevant statistics
- Structure prompts clearly
- Test with different products
- Iterate on prompt templates

### 4. Error Handling

✅ **Do:**
- Handle API failures gracefully
- Provide fallback responses
- Log errors for debugging
- Inform users of issues
- Retry failed requests

---

## Testing

### 1. Test Demo Mode (No API Key Required)

```bash
curl -X POST http://localhost:8000/api/spc/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What can you do?",
    "product_id": 1
  }'
```

Expected: Configuration instructions and feature overview

### 2. Test with OpenAI (Requires API Key)

```bash
export OPENAI_API_KEY="sk-your-key"
export LLM_PROVIDER="openai"

# Restart server
python manage.py runserver 8000

# Test
curl -X POST http://localhost:8000/api/spc/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze the process capability for this product",
    "product_id": 1
  }'
```

Expected: Detailed AI-powered analysis

### 3. Test with Anthropic (Requires API Key)

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key"
export LLM_PROVIDER="anthropic"

# Restart server
python manage.py runserver 8000

# Test
curl -X POST http://localhost:8000/api/spc/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Why is the defect rate high?",
    "product_id": 2
  }'
```

Expected: Detailed troubleshooting with root cause analysis

---

## Migration from Demo to Production

### Step 1: Test in Demo Mode
```bash
LLM_PROVIDER=demo
```

### Step 2: Get API Key
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

### Step 3: Configure Provider
```bash
export LLM_PROVIDER=openai  # or anthropic
export OPENAI_API_KEY="sk-..."
```

### Step 4: Test with Small Dataset
- Use gpt-4o-mini (cheaper)
- Test all 5 intents
- Verify response quality

### Step 5: Monitor Usage
- Check token usage
- Estimate costs
- Set budget limits

### Step 6: Scale Up
- Upgrade to gpt-4o or Claude Opus if needed
- Increase cache timeout for frequently asked questions
- Consider rate limiting for high-traffic scenarios

---

## FAQ

### Q: Which LLM provider should I choose?

**A:**
- **OpenAI GPT-4o-mini**: Best balance of cost and performance
- **OpenAI GPT-4o**: Highest quality, more expensive
- **Anthropic Claude 3.5 Sonnet**: Excellent for complex analysis
- **Anthropic Claude 3 Opus**: Best for nuanced reasoning

### Q: Can I switch between providers?

**A:** Yes! Just change the `LLM_PROVIDER` environment variable and restart the server.

### Q: How much will this cost?

**A:** For typical usage:
- ~100 queries/day with GPT-4o-mini: ~$0.03 - $0.10/day
- ~100 queries/day with Claude 3.5 Sonnet: ~$0.02 - $0.08/day
- Demo mode: FREE

### Q: Is my data secure?

**A:**
- OpenAI and Anthropic have enterprise-grade security
- Data is NOT used for training by default
- Check provider's privacy policy for details
- For sensitive data, consider self-hosted LLMs

### Q: Can I use custom prompts?

**A:** Yes! Edit `backend/apps/spc/services/llm_service.py` and modify the `PromptTemplates` class.

### Q: What if the API is down?

**A:** The system will gracefully fallback to demo mode with an error message.

### Q: Can I track conversation history?

**A:** Yes! Provide a `session_id` in the chat request. History is stored in the `ChatMessage` table.

---

## Support

### Documentation
- OpenAI API: https://platform.openai.com/docs
- Anthropic API: https://docs.anthropic.com

### Troubleshooting Help
1. Check Django logs: `python manage.py runserver 8000`
2. Verify API key is set: `echo $OPENAI_API_KEY`
3. Test API key: Use provider's API console
4. Check status endpoint: `GET /api/spc/chatbot/status/`

### Contributing
To add new LLM providers:
1. Implement provider in `llm_service.py`
2. Add configuration to `settings/dev.py`
3. Update documentation

---

**Version:** 2.0.0
**Last Updated:** 2026-01-11
**Maintained by:** SPC Development Team
