import React, { useState, useEffect } from 'react';
import {
    Box,
    TextField,
    Button,
    Typography,
    Paper,
    CircularProgress,
    Alert,
    useTheme,
    useMediaQuery,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { useParams } from 'react-router-dom';
import { sendChatMessage } from '../api/api';
import { ChatMessage } from '../types/chat';

const ChatBot = () => {
    const { id } = useParams<{ id: string }>();
    const characterId = Number(id);

    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Validate character ID
    useEffect(() => {
        if (!characterId || isNaN(characterId)) {
            setError('Invalid character selected.');
        }
    }, [characterId]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputMessage.trim() || !characterId) return;

        const userMsg: ChatMessage = { role: 'user', content: inputMessage.trim() };
        setMessages((prev) => [...prev, userMsg]);
        setInputMessage('');
        setLoading(true);
        setError('');

        try {
            const res = await sendChatMessage(characterId, inputMessage.trim());
            const aiMsg: ChatMessage = { role: 'assistant', content: res.response };
            setMessages((prev) => [...prev, aiMsg]);
        } catch (err) {
            console.error('Chat error:', err);
            setError('Failed to get response from AI.');
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setMessages([]);
        setError('');
    };

    if (!characterId || isNaN(characterId)) {
        return (
            <Box sx={{ maxWidth: 600, margin: '2rem auto', padding: 2 }}>
                <Alert severity="error">Invalid character ID.</Alert>
            </Box>
        );
    }

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
                variant={isMobile ? 'h5' : 'h4'}
                component="h1"
                align="center"
                gutterBottom
                sx={{ fontWeight: 600 }}
            >
                Chat with AI
            </Typography>

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
                                color: 'text.secondary',
                            }}
                        >
                            <Typography variant="body1">
                                Start a conversation!
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
                                },
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

            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                <Button
                    variant="outlined"
                    color="error"
                    startIcon={<RestartAltIcon />}
                    onClick={handleClear}
                    sx={{ borderRadius: 2 }}
                >
                    Clear Conversation
                </Button>
            </Box>
        </Box>
    );
};

export default ChatBot;
