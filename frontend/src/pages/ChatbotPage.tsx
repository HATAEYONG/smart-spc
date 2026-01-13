import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import {
  MessageCircle,
  Send,
  Bot,
  User,
  Sparkles,
  Lightbulb,
  Brain,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  FileText,
  History
} from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  suggestions?: string[];
  context?: any;
  structuredData?: any;
}

interface ChatHistory {
  id: string;
  title: string;
  date: string;
  messageCount: number;
}

interface QuickQuestion {
  id: string;
  question: string;
  category: string;
  icon: any;
  color: string;
}

export const ChatbotPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      type: 'bot',
      content: '안녕하세요! SPC 품질관리 AI 어시스턴트입니다. 품질 관리에 관한 질문을 해주세요.',
      timestamp: new Date(),
      suggestions: [
        '브레이크 패드 내경의 공정능력은 어떤가요?',
        '최근 발생한 품질 문제를 알려주세요',
        '공정 개선을 위한 제안을 해주세요'
      ]
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sample chat history
  const [chatHistory] = useState<ChatHistory[]>([
    { id: '1', title: '공정능력 분석', date: '2026-01-12', messageCount: 8 },
    { id: '2', title: '불량 원인 분석', date: '2026-01-11', messageCount: 12 },
    { id: '3', title: '세척 공정 개선', date: '2026-01-10', messageCount: 6 },
  ]);

  // Quick questions
  const quickQuestions: QuickQuestion[] = [
    {
      id: '1',
      question: '제품별 공정능력 현황',
      category: '공정능력',
      icon: TrendingUp,
      color: 'bg-blue-100 text-blue-700'
    },
    {
      id: '2',
      question: '최근 품질 이슈 요약',
      category: '품질이슈',
      icon: AlertCircle,
      color: 'bg-orange-100 text-orange-700'
    },
    {
      id: '3',
      question: '개선 제안 받기',
      category: '개선제안',
      icon: Lightbulb,
      color: 'bg-green-100 text-green-700'
    },
    {
      id: '4',
      question: 'AI Run Rule 위반 내역',
      category: 'SPC분석',
      icon: CheckCircle,
      color: 'bg-purple-100 text-purple-700'
    },
  ];

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (suggestion?: string) => {
    const messageText = suggestion || inputMessage.trim();
    if (!messageText) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simulate bot response (in real app, this would call an API)
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: getBotResponse(messageText),
        timestamp: new Date(),
        suggestions: [
          '더 자세한 분석을 원하시나요?',
          '관련 차트를 보여주세요',
          '개선 방안을 제안해주세요'
        ],
      };

      setMessages(prev => [...prev, botMessage]);
      setIsLoading(false);
      inputRef.current?.focus();
    }, 1000);
  };

  const getBotResponse = (question: string): string => {
    // Sample bot responses based on keywords
    if (question.includes('공정능력') || question.includes('Cpk')) {
      return `**공정능력 분석 결과**

현재 브레이크 패드 제품의 공정능력 현황입니다:

| 특성 | Cpk | 상태 |
|------|-----|------|
| 내경 | 1.45 | ✅ 우수 |
| 외경 | 1.28 | ⚠️ 양호 |
| 두께 | 0.95 | ❌ 개선필요 |
| 깊이 | 0.72 | ❌ 부족 |

**권장 사항:**
- 두께 특성의 공정능력이 1.0 미만입니다. 즉각적인 개선 조치가 필요합니다.
- 내경은 6시그마 수준에 근접하여 현재 수준 유지가 권장됩니다.`;
    } else if (question.includes('불량') || question.includes('문제')) {
      return `**최근 품질 문제 요약**

📊 **주요 불량 현황 (최근 7일)**

1. **치수불량** (42%) - 가장 높은 비중
   - 주로 내경 규격 이탈
   - 원인: 공구 마모도 누적

2. **이물불량** (28%)
   - 세척 공정 미흡
   - 개선안: 세척 시간 3분→5분 연장

3. **외관불량** (18%)
   - 스크래치, 흠집
   - 취급 프로세스 개선 필요

4. **기타** (12%)
   - 균열, 변색 등

**긴급 조치 항목:** 열처리 로 온도 편차로 인한 균열 불량 리스크 상승中`;
    } else if (question.includes('개선') || question.includes('제안')) {
      return `**공정 개선 제안**

🎯 **우선순위별 개선 과제**

**[긴급] 열처리 로 온도 제어**
- 예상 효과: 균열 불량률 1.2% → 0.3% 감소
- 조치: 열전대 교체, 온도 제어 파라미터 재튜닝
- 예상 비용: 500만원
- ROI: 850%

**[높음] 세척 공정 최적화**
- 예상 효과: 이물 불량률 8% → 2% 감소
- 조치: 초음파 세척 시간 연장 (3분→5분)
- 예상 비용: 설비 개조 200만원
- 연간 절감액: 1.2억원

**[중간] 공구 교체 주기 최적화**
- 예상 효과: 치수불량 15% 감소
- 조치: 교체 주기 50시간→40시간 단축
- 예상 비용: 추가 공구비 월 50만원
- 효과: 불량 감소으로 품질비용 절감`;
    } else {
      return `질문해 주셔서 감사합니다.

해당 내용에 대해 분석한 결과입니다:

**주요 insight:**
- 현재 공정은 전반적으로 안정적인 상태입니다
- 일부 특성에서 개선 여지가 있습니다
- 정기적인 모니터링이 권장됩니다

더 자세한 분석이 필요하시면 말씀해 주세요.`;
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const stats = {
    totalConversations: chatHistory.length,
    totalMessages: messages.length,
    avgResponseTime: '1.2초',
    satisfactionRate: '94%',
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Brain className="w-8 h-8 text-purple-600" />
            AI 챗봇
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            SPC 품질관리 AI 어시스턴트
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <History className="w-4 h-4 mr-2" />
            대화 기록
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <FileText className="w-4 h-4 mr-2" />
            대화 내보내기
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-purple-100 mb-1">총 대화 수</div>
                <div className="text-3xl font-bold">{stats.totalConversations}건</div>
              </div>
              <MessageCircle className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">메시지 수</div>
                <div className="text-2xl font-bold text-gray-900">{stats.totalMessages}건</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">평균 응답 시간</div>
                <div className="text-2xl font-bold text-gray-900">{stats.avgResponseTime}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">만족도</div>
                <div className="text-2xl font-bold text-green-600">{stats.satisfactionRate}</div>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500 opacity-50" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 왼쪽 사이드바: 빠른 질문 & 대화 기록 */}
        <div className="lg:col-span-1 space-y-6">
          {/* 빠른 질문 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Sparkles className="w-5 h-5 text-purple-600" />
                빠른 질문
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {quickQuestions.map((qq) => {
                  const Icon = qq.icon;
                  return (
                    <button
                      key={qq.id}
                      onClick={() => handleSendMessage(qq.question)}
                      disabled={isLoading}
                      className="w-full p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 text-left transition-all disabled:opacity-50"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <div className={`p-1 rounded ${qq.color}`}>
                          <Icon className="w-3 h-3" />
                        </div>
                        <span className="text-xs font-medium text-gray-500">{qq.category}</span>
                      </div>
                      <div className="text-sm text-gray-900">{qq.question}</div>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* 대화 기록 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <History className="w-5 h-5 text-purple-600" />
                최근 대화
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {chatHistory.map((chat) => (
                  <button
                    key={chat.id}
                    className="w-full p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 text-left transition-all"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">{chat.title}</span>
                      <Badge variant="outline" className="text-xs">{chat.messageCount}건</Badge>
                    </div>
                    <div className="text-xs text-gray-500">{chat.date}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 메인 채팅 영역 */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <CardHeader className="border-b">
              <CardTitle className="flex items-center gap-2">
                <Bot className="w-5 h-5 text-purple-600" />
                SPC 품질관리 AI 어시스턴트
                <Badge className="bg-green-100 text-green-700 ml-2">Online</Badge>
              </CardTitle>
            </CardHeader>

            {/* Messages Area */}
            <CardContent className="flex-1 overflow-y-auto py-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse space-x-2' : 'flex-row space-x-2'}`}>
                      {/* Avatar */}
                      {message.type === 'bot' && (
                        <div className="flex-shrink-0 w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                          <Bot className="w-4 h-4 text-white" />
                        </div>
                      )}

                      {/* Message Content */}
                      <div className="flex-1">
                        {/* Message Bubble */}
                        <div className={`inline-block px-4 py-3 rounded-2xl ${
                          message.type === 'user'
                            ? 'bg-blue-500 text-white rounded-br-sm'
                            : 'bg-gray-100 text-gray-900 rounded-bl-sm'
                        }`}>
                          <div className="text-sm whitespace-pre-wrap leading-relaxed">
                            {message.content}
                          </div>
                        </div>

                        {/* Timestamp */}
                        <p className={`text-xs text-gray-500 mt-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                          {message.timestamp.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                        </p>

                        {/* Suggestions */}
                        {message.suggestions && message.suggestions.length > 0 && message.type === 'bot' && (
                          <div className="mt-3 space-y-2">
                            {message.suggestions.map((suggestion, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleSendMessage(suggestion)}
                                disabled={isLoading}
                                className="w-full text-left px-3 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-lg text-xs font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-start gap-2 group"
                              >
                                <Lightbulb className="w-3 h-3 text-purple-600 flex-shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                                <span className="flex-1">{suggestion}</span>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* User Avatar */}
                      {message.type === 'user' && (
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                          <User className="w-4 h-4 text-white" />
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Loading Indicator */}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex space-x-2">
                      <div className="flex-shrink-0 w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="px-4 py-3 bg-gray-100 rounded-2xl rounded-bl-sm">
                        <div className="flex space-x-2 items-center">
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </CardContent>

            {/* Input Area */}
            <div className="border-t p-4">
              <div className="flex space-x-2">
                <Input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="질문을 입력하세요..."
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  onClick={() => handleSendMessage()}
                  disabled={isLoading || !inputMessage.trim()}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                💡 팁: Enter 키로 메시지를 전송할 수 있습니다
              </p>
            </div>
          </Card>
        </div>
      </div>

      {/* AI 능력 안내 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-600" />
            AI 어시스턴트 능력
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-blue-900">공정능력 분석</span>
              </div>
              <p className="text-sm text-blue-800">
                Cp, Cpk, Pp, Ppk 지수 분석 및 Six Sigma 수준 평가
              </p>
            </div>

            <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-5 h-5 text-orange-600" />
                <span className="font-semibold text-orange-900">품질 문제 진단</span>
              </div>
              <p className="text-sm text-orange-800">
                불량 원인 분석 및 Run Rule 위반 패턴 식별
              </p>
            </div>

            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="w-5 h-5 text-green-600" />
                <span className="font-semibold text-green-900">개선 제안</span>
              </div>
              <p className="text-sm text-green-800">
                데이터 기반의 최적화 방안 및 Best Practice 제공
              </p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-5 h-5 text-purple-600" />
                <span className="font-semibold text-purple-900">보고서 생성</span>
              </div>
              <p className="text-sm text-purple-800">
                분석 결과 요약 및 자동 보고서 작성 지원
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChatbotPage;
