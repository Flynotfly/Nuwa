import React, { useState } from 'react';

const ChatBot = () => {
    // Context settings (optional)
    const [scenario, setScenario] = useState('');
    const [personality, setPersonality] = useState('');
    const [exampleDialogs, setExampleDialogs] = useState('');

    // Chat state
    const [messages, setMessages] = useState([]); // [{role: 'user'|'assistant', content: '...'}]
    const [inputMessage, setInputMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) return;

        const userMsg = { role: 'user', content: inputMessage.trim() };
        const newMessages = [...messages, userMsg];
        setMessages(newMessages);
        setInputMessage('');
        setLoading(true);
        setError('');

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add CSRF token if using Django session auth
                    // 'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    message: inputMessage.trim(),
                    scenario: scenario.trim(),
                    personality: personality.trim(),
                    example_dialogs: exampleDialogs.trim(),
                    history: messages, // full history sent each time
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const data = await response.json();
            const aiMsg = { role: 'assistant', content: data.response };
            setMessages((prev) => [...prev, aiMsg]);
        } catch (err) {
            setError(`Failed to get response: ${err.message}`);
            // Optionally remove user message on failure? Or keep it.
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setMessages([]);
        setScenario('');
        setPersonality('');
        setExampleDialogs('');
        setError('');
    };

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
            <h2>Ollama Chatbot</h2>

            {/* Context Settings */}
            <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
                <h3>AI Context (Optional)</h3>
                <label>
                    Scenario:
                    <textarea
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value)}
                        placeholder="e.g., You are a fitness coach..."
                        style={{ width: '100%', height: '60px', marginTop: '5px' }}
                    />
                </label>
                <br />
                <label>
                    Personality:
                    <input
                        type="text"
                        value={personality}
                        onChange={(e) => setPersonality(e.target.value)}
                        placeholder="e.g., Friendly, professional, concise"
                        style={{ width: '100%', marginTop: '5px' }}
                    />
                </label>
                <br />
                <label>
                    Example Dialogs:
                    <textarea
                        value={exampleDialogs}
                        onChange={(e) => setExampleDialogs(e.target.value)}
                        placeholder={`User: Hello\nAssistant: Hi there!`}
                        style={{ width: '100%', height: '80px', marginTop: '5px' }}
                    />
                </label>
                <button
                    type="button"
                    onClick={handleClear}
                    style={{ marginTop: '10px', padding: '5px 10px', backgroundColor: '#ff6b6b', color: 'white', border: 'none', borderRadius: '4px' }}
                >
                    Clear All
                </button>
            </div>

            {/* Chat History */}
            <div style={{ height: '400px', overflowY: 'auto', border: '1px solid #ccc', padding: '10px', marginBottom: '10px', borderRadius: '8px' }}>
                {messages.length === 0 ? (
                    <p style={{ color: '#888' }}>No messages yet. Start a conversation!</p>
                ) : (
                    messages.map((msg, idx) => (
                        <div
                            key={idx}
                            style={{
                                textAlign: msg.role === 'user' ? 'right' : 'left',
                                marginBottom: '10px',
                            }}
                        >
                            <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong>
                            <div
                                style={{
                                    display: 'inline-block',
                                    padding: '8px 12px',
                                    backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#f1f1f1',
                                    borderRadius: '12px',
                                    maxWidth: '80%',
                                    wordWrap: 'break-word',
                                }}
                            >
                                {msg.content}
                            </div>
                        </div>
                    ))
                )}
                {loading && (
                    <div style={{ textAlign: 'left' }}>
                        <strong>AI:</strong>
                        <div style={{ display: 'inline-block', padding: '8px 12px', backgroundColor: '#f1f1f1', borderRadius: '12px' }}>
                            Thinking...
                        </div>
                    </div>
                )}
                {error && (
                    <div style={{ color: 'red', marginTop: '10px' }}>
                        ❌ {error}
                    </div>
                )}
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit}>
        <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            rows="3"
            style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #ccc' }}
            disabled={loading}
        />
                <button
                    type="submit"
                    disabled={loading || !inputMessage.trim()}
                    style={{
                        marginTop: '10px',
                        padding: '10px 20px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                    }}
                >
                    {loading ? 'Sending...' : 'Send'}
                </button>
            </form>
        </div>
    );
};

export default ChatBot;