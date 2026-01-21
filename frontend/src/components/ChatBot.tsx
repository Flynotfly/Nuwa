// components/ChatBot.tsx
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
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from '@mui/icons-material/Send';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { useParams, useNavigate } from 'react-router-dom'; // 👈 add useNavigate
import { getChatDetail, sendChatMessage } from '../api/api'; // 👈 adjust import path
import { ChatMessage } from '../types/chatting';
import { ChatDetail } from '../types/chat'; // 👈 ensure this exists

const ChatBot = () => {
  const { id } = useParams<{ id: string }>();
  const chatId = Number(id);
  const navigate = useNavigate();

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [chatDetail, setChatDetail] = useState<ChatDetail | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPrompt, setShowPrompt] = useState(false);

  // Validate and fetch chat on mount
  useEffect(() => {
    if (!chatId || isNaN(chatId)) {
      setError('Invalid chat ID.');
      return;
    }

    const fetchChat = async () => {
      try {
        const detail = await getChatDetail(chatId);
        setChatDetail(detail);

        // Optional: load existing messages if your backend supports it
        // For now, we start fresh per session (as in your current logic)
        // If you store message history, fetch it here
      } catch (err) {
        console.error('Failed to load chat:', err);
        setError('Could not load chat. It may not exist or you lack permission.');
      }
    };

    fetchChat();
  }, [chatId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !chatId) return;

    const userMsg: ChatMessage = { role: 'user', content: inputMessage.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);
    setError('');

    try {
      // ✅ Send message using CHAT ID (not character ID)
      const res = await sendChatMessage(chatId, inputMessage.trim());
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

  if (!chatId || isNaN(chatId)) {
    return (
      <Box sx={{ maxWidth: 600, margin: '2rem auto', padding: 2 }}>
        <Alert severity="error">Invalid chat ID.</Alert>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ maxWidth: 600, margin: '2rem auto', padding: 2 }}>
        <Alert severity="error" onClose={() => navigate('/')} sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="outlined" onClick={() => navigate('/')}>
          Back to Characters
        </Button>
      </Box>
    );
  }

  if (!chatDetail) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="70vh">
        <CircularProgress />
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
        Chat with {chatDetail.character_name}
      </Typography>

      {chatDetail && (
        <Paper
          elevation={1}
          sx={{
            p: 2,
            backgroundColor: theme.palette.grey[50],
            borderRadius: 2,
            maxWidth: '100%',
          }}
        >
          <Typography variant="subtitle2" gutterBottom color="text.secondary">
            About {chatDetail.character_name}
          </Typography>
          <Typography variant="body2" paragraph>
            {chatDetail.description || 'No description available.'}
          </Typography>

          {!chatDetail.is_hidden_prompt && chatDetail.system_prompt && (
            <>
              <Box
                sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
                onClick={() => setShowPrompt(!showPrompt)}
              >
                <Typography variant="subtitle2" color="text.secondary">
                  Personality
                </Typography>
                <ExpandMoreIcon
                  sx={{
                    transform: showPrompt ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.2s',
                    ml: 0.5,
                  }}
                />
              </Box>
              {showPrompt && (
                <Typography
                  variant="body2"
                  sx={{
                    fontStyle: 'italic',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    mt: 1,
                  }}
                >
                  "{chatDetail.system_prompt}"
                </Typography>
              )}
            </>
          )}
        </Paper>
      )}

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
                Start a conversation with {chatDetail.character_name}!
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
              placeholder={`Message ${chatDetail.character_name}...`}
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