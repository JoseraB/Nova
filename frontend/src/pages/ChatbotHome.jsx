import React, { useRef, useState, useEffect } from "react";
import { assets } from "../assets/assets";
import axios from "axios";

const ChatbotHome = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [hasStartedChat, setHasStartedChat] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const textareaRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e);
    }
  };

  const goBack = () => {
    setHasStartedChat(false);
    setMessages([]);
    setMessage("");
    setError(null);
  }

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userMessage = message.trim();
    setMessage("");
    setError(null);

    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    if (!hasStartedChat) {
      setHasStartedChat(true);
    }

    setIsLoading(true);

    try {
      if (!Array.isArray(messages)) {
        throw new Error("Invalid Messages");
      }
      const response = await axios.post("https://nova-vy9s.onrender.com/openai", {
        messages: [...messages, { role: "user", content: userMessage }],
      });

      if (response.status !== 200) throw new Error("Failed to send message");

      const data = await response.data;

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.message },
      ]);
    } catch (e) {
      console.error("Error:", e);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I am unable to assist you at the moment. Please try again later.",
        },
      ]);
    } finally {
      setIsLoading(false);

      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const renderLoadingIndicator = () => {
    if (!isLoading) return null;

    return (
      <div className="flex justify-start mb-3 overflow-hidden">
        <div className="bg-gray-200 text-black p-3 rounded-xl flex items-center">
          <div className="flex space-x-1">
            <div
              className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
              style={{ animationDelay: "0s" }}
            ></div>
            <div
              className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
              style={{ animationDelay: "0.2s" }}
            ></div>
            <div
              className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
              style={{ animationDelay: "0.4s" }}
            ></div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full h-screen relative flex flex-col overflow-hidden">
      {!hasStartedChat ? (
        <div className="flex-1 flex justify-center items-center overflow-hidden">
          <img
            src={assets.NOVA}
            alt="NOVA"
            className="object-contain w-[80vw] h-[80vw] opacity-70"
          />
          <div className="absolute top-0 left-0 w-full h-full flex flex-col items-center justify-center space-y-5">
            <div className="flex items-center space-x-5">
              <img
                src={assets.Knight}
                alt="Knight"
                className="w-[6.5em] h-[6em]"
              />
              <h1 className="text-6xl md:text-8xl font-bold tracking-wider">
                NOVA
              </h1>
            </div>
            <div className="w-full max-w-2xl px-4">
              <form onSubmit={onSubmit} className="flex flex-col">
                <textarea
                  ref={textareaRef}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Hi! What can I assist you with today?"
                  className="border-2 border-gray-300 rounded-2xl px-4 py-3 min-h-40 bg-gray-100 shadow-md resize-none"
                  rows={4}
                  aria-label="Message input"
                />
                <button
                  type="submit"
                  className="mt-3 bg-blue-500 text-white px-4 py-2 rounded-xl self-end hover:bg-blue-600 transition-colors"
                >
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col p-4 overflow-hidden">
          <button className="absolute top-4 left-4 bg-blue-500 text-white px-4 py-2 rounded-md self-end hover:bg-blue-600 transition-colors" onClick={() => goBack()} aria-label="Go back">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8"/>
            </svg>
          </button>
          <div className="items-center justify-center pl-28">
            <img
              src={assets.NOVA}
              alt="NOVA"
              className="absolute object-contain w-[80vw] h-[80vw] opacity-70 -z-10"
              aria-hidden="true"
            />
          </div>
          <div
            ref={messagesContainerRef}
            className="flex-1 flex flex-col space-y-4 overflow-y-auto mb-4 p-2"
          >
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-3/4 p-3 rounded-xl ${
                    msg.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 text-black"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {renderLoadingIndicator()}

            {error && (
              <div className="text-red-500 text-center py-2">{error}</div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <form
            onSubmit={onSubmit}
            className="flex items-center space-x-2 mt-auto"
          >
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="flex-1 border-2 border-gray-300 rounded-2xl px-4 py-2 min-h-12 max-h-40 bg-gray-100 shadow-md resize-none"
              rows={1}
              disabled={isLoading}
              aria-label="Message input"
            />
            <button
              type="submit"
              className={`p-3 rounded-full bg-blue-500 text-white ${
                isLoading
                  ? "opacity-50 cursor-not-allowed"
                  : "hover:bg-blue-600"
              }`}
              disabled={isLoading}
              aria-label="Send message"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatbotHome;
