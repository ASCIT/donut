import React, { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// ChatGPT-style logo icon
const LogoIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z"/>
  </svg>
)

// Arrow up icon for send button
const SendIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="19" x2="12" y2="5"></line>
    <polyline points="5 12 12 5 19 12"></polyline>
  </svg>
)

// Suggestion prompts
const SUGGESTIONS = [
  {
    title: 'Email & Mailing Lists',
    desc: 'Troubleshoot sending or receiving issues',
    prompt: "I want to send an email to a group but it's not showing up in my list. How can I fix this?"
  },
  {
    title: 'Manage Positions',
    desc: 'Add or remove people from roles',
    prompt: 'How do I add someone as a position holder in a group?'
  },
  {
    title: 'Understand Permissions',
    desc: 'Learn about Send, Receive & Manage',
    prompt: "What's the difference between Send, Receive, and Manage permissions for positions?"
  },
  {
    title: 'Create Mailing List',
    desc: 'Set up a new group with email',
    prompt: 'How do I create a new mailing list for my committee?'
  }
]

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingContent])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [input])

  const sendMessage = async (text) => {
    if (!text.trim() || isLoading) return

    const userMessage = { role: 'user', content: text.trim() }
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInput('')
    setIsLoading(true)
    setStreamingContent('')

    try {
      const response = await fetch('/gpt-sam/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to get response')
      }

      const data = await response.json()

      // Simulate streaming by revealing text progressively
      const fullText = data.response
      let currentIndex = 0
      const chunkSize = 4

      const streamInterval = setInterval(() => {
        currentIndex += chunkSize
        if (currentIndex >= fullText.length) {
          clearInterval(streamInterval)
          setStreamingContent('')
          setMessages([...newMessages, { role: 'assistant', content: fullText }])
          setIsLoading(false)
        } else {
          setStreamingContent(fullText.substring(0, currentIndex))
        }
      }, 8)

    } catch (error) {
      setMessages([...newMessages, {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}`
      }])
      setIsLoading(false)
      setStreamingContent('')
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  // Get user initial for avatar
  const getUserInitial = () => {
    return 'U'
  }

  return (
    <div className="chat-container">
      {/* Messages Area */}
      <div className="messages-viewport">
        {messages.length === 0 && !isLoading ? (
          <div className="welcome-screen">
            <div className="welcome-logo">
              <LogoIcon />
            </div>
            <h1 className="welcome-title">How can I help you today?</h1>

            <div className="suggestions-container">
              {SUGGESTIONS.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-btn"
                  onClick={() => sendMessage(suggestion.prompt)}
                >
                  <p className="suggestion-title">{suggestion.title}</p>
                  <p className="suggestion-desc">{suggestion.desc}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div key={index} className={`message-row ${message.role}`}>
                <div className="message-content">
                  <div className={`avatar ${message.role}`}>
                    {message.role === 'assistant' ? (
                      <LogoIcon />
                    ) : (
                      getUserInitial()
                    )}
                  </div>
                  <div className="message-text">
                    {message.role === 'assistant' ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                    ) : (
                      <p>{message.content}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Streaming response */}
            {isLoading && streamingContent && (
              <div className="message-row assistant">
                <div className="message-content">
                  <div className="avatar assistant">
                    <LogoIcon />
                  </div>
                  <div className="message-text">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{streamingContent}</ReactMarkdown>
                  </div>
                </div>
              </div>
            )}

            {/* Loading indicator */}
            {isLoading && !streamingContent && (
              <div className="message-row assistant">
                <div className="message-content">
                  <div className="avatar assistant">
                    <LogoIcon />
                  </div>
                  <div className="message-text">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-container">
        <div className="input-wrapper">
          <form onSubmit={handleSubmit} className="input-box">
            <textarea
              ref={textareaRef}
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message GPT-SAM..."
              rows={1}
              disabled={isLoading}
            />
          </form>
          <button
            type="submit"
            className="send-btn"
            disabled={!input.trim() || isLoading}
            onClick={handleSubmit}
          >
            <SendIcon />
          </button>
        </div>
      </div>
    </div>
  )
}
