// src/components/ChatBot.jsx
import React, { useState } from 'react';
import axios from 'axios';
import {
    Box,
    TextField,
    Button,
    Typography,
    Paper,
    FormControl,
    InputLabel,
    OutlinedInput,
    FormHelperText,
    CircularProgress,
    Alert,
    useTheme,
    useMediaQuery,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

const ChatBot = () => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    // Context settings
    const [scenario, setScenario] = useState('');
    const [personality, setPersonality] = useState('');
    const [exampleDialogs, setExampleDialogs] = useState('');

    // Chat state
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) return;

        const userMsg = { role: 'user', content: inputMessage.trim() };
        setMessages(prev => [...prev, userMsg]);
        setInputMessage('');
        setLoading(true);
        setError('');

        try {
            const response = await axios.post('http://localhost:8000/chat', {
                message: inputMessage.trim(),
                scenario: scenario.trim(),
                personality: personality.trim(),
                example_dialogs: exampleDialogs.trim(),
                history: messages,
            }, {
                headers: {
                    'Content-Type': 'application/json',
                },
                timeout: 30000,
            });

            const aiMsg = { role: 'assistant', content: response.data.response };
            setMessages(prev => [...prev, aiMsg]);
        } catch (err) {
            console.error('Chat API error:', err);
            const errorMsg = err.response?.data?.error ||
                err.message ||
                'Failed to get response from AI service';
            setError(errorMsg);
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
        <Box
            sx={{
                maxWidth: 900,
                margin: '0 auto',
                padding: { xs: 2, md: 3 },
                display: 'flex',
                flexDirection: 'column',
                gap: 3,
            }}
        >
            <Typography
                variant={isMobile ? "h5" : "h4"}
                component="h1"
                align="center"
                gutterBottom
                sx={{ fontWeight: 600 }}
            >
                Ollama AI Chatbot
            </Typography>

            {/* Context Settings Panel */}
            <Paper
                elevation={3}
                sx={{
                    padding: 2.5,
                    borderRadius: 2,
                    backgroundColor: theme.palette.background.paper,
                }}
            >
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 500 }}>
                    AI Personality Settings
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                    <FormControl fullWidth>
                        <InputLabel htmlFor="scenario">Scenario</InputLabel>
                        <OutlinedInput
                            id="scenario"
                            label="Scenario"
                            value={scenario}
                            onChange={(e) => setScenario(e.target.value)}
                            placeholder="e.g., You're a fitness coach helping with workout plans"
                            multiline
                            rows={2}
                            sx={{ borderRadius: 2 }}
                        />
                    </FormControl>

                    <FormControl fullWidth>
                        <InputLabel htmlFor="personality">Personality</InputLabel>
                        <OutlinedInput
                            id="personality"
                            label="Personality"
                            value={personality}
                            onChange={(e) => setPersonality(e.target.value)}
                            placeholder="e.g., Friendly, knowledgeable, and motivational"
                            sx={{ borderRadius: 2 }}
                        />
                    </FormControl>

                    <FormControl fullWidth>
                        <InputLabel htmlFor="examples">Example Dialogs</InputLabel>
                        <OutlinedInput
                            id="examples"
                            label="Example Dialogs"
                            value={exampleDialogs}
                            onChange={(e) => setExampleDialogs(e.target.value)}
                            placeholder={`User: How do I start?\nAssistant: First, tell me your goals!`}
                            multiline
                            rows={3}
                            sx={{ borderRadius: 2 }}
                        />
                        <FormHelperText>
                            Show the AI how conversations should flow
                        </FormHelperText>
                    </FormControl>

                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                        <Button
                            variant="outlined"
                            color="error"
                            startIcon={<RestartAltIcon />}
                            onClick={handleClear}
                            sx={{ borderRadius: 2 }}
                        >
                            Clear Settings
                        </Button>
                    </Box>
                </Box>
            </Paper>

            {/* Chat Interface */}
            <Paper
                elevation={3}
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    height: 500,
                    borderRadius: 2,
                    overflow: 'hidden',
                    backgroundColor: theme.palette.background.default,
                }}
            >
                {/* Messages Area */}
                <Box
                    sx={{
                        flex: 1,
                        overflowY: 'auto',
                        padding: 2,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 1.5,
                    }}
                >
                    {messages.length === 0 ? (
                        <Box
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                height: '100%',
                                color: 'text.secondary'
                            }}
                        >
                            <Typography variant="body1">
                                Start a conversation with the AI assistant
                            </Typography>
                        </Box>
                    ) : (
                        messages.map((msg, idx) => (
                            <Box
                                key={idx}
                                sx={{
                                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                                    maxWidth: '85%',
                                }}
                            >
                                <Box
                                    sx={{
                                        backgroundColor:
                                            msg.role === 'user'
                                                ? theme.palette.primary.main
                                                : theme.palette.grey[200],
                                        color:
                                            msg.role === 'user'
                                                ? theme.palette.primary.contrastText
                                                : theme.palette.text.primary,
                                        padding: 1.5,
                                        borderRadius: 2,
                                        borderTopLeftRadius: msg.role === 'user' ? 2 : 0,
                                        borderTopRightRadius: msg.role === 'user' ? 0 : 2,
                                        wordBreak: 'break-word',
                                        whiteSpace: 'pre-wrap',
                                    }}
                                >
                                    {msg.content}
                                </Box>
                            </Box>
                        ))
                    )}

                    {loading && (
                        <Box sx={{ alignSelf: 'flex-start', maxWidth: '85%' }}>
                            <Box
                                sx={{
                                    backgroundColor: theme.palette.grey[200],
                                    padding: 1.5,
                                    borderRadius: 2,
                                    borderTopRightRadius: 0,
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 1,
                                }}
                            >
                                <CircularProgress size={20} />
                                <Typography variant="body2">AI is thinking...</Typography>
                            </Box>
                        </Box>
                    )}

                    {error && (
                        <Alert
                            severity="error"
                            onClose={() => setError('')}
                            sx={{ alignSelf: 'center', width: '100%' }}
                        >
                            {error}
                        </Alert>
                    )}
                </Box>

                {/* Input Area */}
                <Box
                    component="form"
                    onSubmit={handleSubmit}
                    sx={{
                        padding: 2,
                        borderTop: `1px solid ${theme.palette.divider}`,
                        backgroundColor: theme.palette.background.paper,
                    }}
                >
                    <Box sx={{ display: 'flex', gap: 1.5 }}>
                        <TextField
                            fullWidth
                            variant="outlined"
                            size="small"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder="Type your message..."
                            disabled={loading}
                            multiline
                            maxRows={3}
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    borderRadius: 2,
                                }
                            }}
                        />
                        <Button
                            type="submit"
                            variant="contained"
                            disabled={loading || !inputMessage.trim()}
                            sx={{
                                borderRadius: 2,
                                minWidth: { xs: 'auto', sm: 100 },
                                padding: '8px 16px',
                            }}
                            endIcon={<SendIcon />}
                        >
                            {isMobile ? 'Send' : 'Send Message'}
                        </Button>
                    </Box>
                </Box>
            </Paper>
        </Box>
    );
};

export default ChatBot;