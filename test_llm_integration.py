"""
LLM Integration Test Script
Tests the LLM service without needing the full Django server
"""
import os
import sys
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

import django
django.setup()

from apps.spc.services.llm_service import get_spc_chatbot_service, LLMProvider, PromptTemplates


def test_llm_service():
    """Test LLM service functionality"""
    print("=" * 60)
    print("LLM Integration Test")
    print("=" * 60)

    # Get service instance
    chatbot_service = get_spc_chatbot_service()

    # Test 1: Provider Status
    print("\n[Test 1] Provider Status")
    print("-" * 60)
    status = chatbot_service.get_provider_status()
    print(f"Provider: {status['provider']}")
    print(f"Model: {status['model']}")
    print(f"Configured: {status['configured']}")
    print(f"API Key Set: {status['api_key_set']}")

    # Test 2: Demo Mode Response
    print("\n[Test 2] Demo Mode Response")
    print("-" * 60)
    test_message = "What can you do?"

    context_data = {
        'user_message': test_message,
    }

    result = chatbot_service.chat(
        user_message=test_message,
        intent='general',
        context_data=context_data,
        conversation_history=None
    )

    print(f"Response (first 200 chars):")
    print(result['response'][:200] + "...")

    # Test 3: Capability Analysis Template
    print("\n[Test 3] Capability Analysis Template")
    print("-" * 60)

    template_context = {
        'product_name': 'M10 Bolt',
        'cp': 2.13,
        'cpk': 1.70,
        'usl': 10.5,
        'lsl': 9.5,
        'target': 10.0,
        'mean': 10.0961,
        'std_dev': 0.1167,
        'sample_size': 150,
        'is_normal': 'Yes',
        'oos_rate': 0.0267,
        'user_message': 'Analyze the process capability'
    }

    try:
        formatted_template = PromptTemplates.CAPABILITY_ANALYSIS_TEMPLATE.format(**template_context)
        print(f"Template formatted successfully!")
        print(f"Template length: {len(formatted_template)} characters")
    except Exception as e:
        print(f"Error formatting template: {e}")

    # Test 4: All Templates
    print("\n[Test 4] All Templates Format Check")
    print("-" * 60)

    templates = {
        'capability_analysis': PromptTemplates.CAPABILITY_ANALYSIS_TEMPLATE,
        'troubleshooting': PromptTemplates.TROUBLESHOOTING_TEMPLATE,
        'trend_analysis': PromptTemplates.TREND_ANALYSIS_TEMPLATE,
        'root_cause': PromptTemplates.ROOT_CAUSE_TEMPLATE,
        'improvement': PromptTemplates.IMPROVEMENT_TEMPLATE,
        'general': PromptTemplates.GENERAL_QUERY_TEMPLATE,
    }

    for name, template in templates.items():
        try:
            # Test with minimal context
            test_context = {'user_message': 'test', 'product_name': 'Test Product'}
            formatted = template.format(**{k: v for k, v in test_context.items() if k in template or '{' + k + '}' in template})
            print(f"✅ {name}: OK ({len(formatted)} chars)")
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")

    # Test 5: Message Building
    print("\n[Test 5] Message Building")
    print("-" * 60)

    messages = chatbot_service.llm_service.build_messages(
        template=PromptTemplates.GENERAL_QUERY_TEMPLATE,
        context={'user_message': 'Hello, what can you help with?'},
        conversation_history=None
    )

    print(f"Number of messages: {len(messages)}")
    for i, msg in enumerate(messages):
        print(f"Message {i+1}: role={msg.role}, content_length={len(msg.content)}")

    # Test 6: Cost Estimation
    print("\n[Test 6] Cost Estimation (if configured)")
    print("-" * 60)

    if status['configured'] and status['provider'] != 'demo':
        # Test a simple query
        result = chatbot_service.chat(
            user_message="What is SPC?",
            intent='general',
            context_data={'user_message': 'What is SPC?'},
            conversation_history=None
        )

        if result.get('tokens_used'):
            print(f"Tokens used: {result['tokens_used']}")
            print(f"Estimated cost: ${result['cost_estimate']:.6f}")
        else:
            print("No token usage returned (demo mode or error)")
    else:
        print("Skipping - Demo mode or not configured")

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Provider: {status['provider']}")
    print(f"Status: {'✅ READY' if status['configured'] or status['provider'] == 'demo' else '❌ NOT CONFIGURED'}")

    if status['provider'] == 'demo':
        print("\n📝 Note: Running in DEMO mode")
        print("To enable full AI capabilities, configure an API key:")
        print("  export LLM_PROVIDER=openai")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  # or")
        print("  export LLM_PROVIDER=anthropic")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
    elif status['configured']:
        print("\n✅ LLM service is fully configured and ready!")
        print(f"Model: {status['model']}")

    print("\n" + "=" * 60)


def test_api_endpoints():
    """Test API endpoints (requires server running)"""
    print("\n\nAPI Endpoint Tests")
    print("=" * 60)
    print("Note: These tests require the Django server to be running")
    print("Start with: python manage.py runserver 8000")
    print("\nTest URLs:")
    print("  1. GET  http://localhost:8000/api/spc/chatbot/status/")
    print("  2. GET  http://localhost:8000/api/spc/chatbot/capabilities/")
    print("  3. POST http://localhost:8000/api/spc/chatbot/chat/")
    print("\nExample chat request:")
    print("""curl -X POST http://localhost:8000/api/spc/chatbot/chat/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Analyze process capability for product 1",
    "product_id": 1
  }'""")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_llm_service()
        test_api_endpoints()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
