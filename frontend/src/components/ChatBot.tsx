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
  Snackbar,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from '@mui/icons-material/Send';
import dayjs from 'dayjs';
import { useParams } from 'react-router-dom';
import { getChatDetail, getAllMessages, sendChatMessage } from '../api/api';
import { ChatMessage } from '../types/chatting';
import { ChatDetail } from '../types/chat';

const ChatBot = () => {
  const { id } = useParams<{ id: string }>();
  const chatId = Number(id);

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [chatDetail, setChatDetail] = useState<ChatDetail | null>(null);
  const [allMessages, setAllMessages] = useState<ChatMessage[]>([]);
  const [lastMessageId, setLastMessageId] = useState<number | null>(null)
  const [currentMessages, setCurrentMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    if (!chatId || isNaN(chatId)) {
      setError('Invalid chat ID.');
      return;
    }
    const loadAll = async () => {
      await Promise.all([
        fetchChatDetail(),
        fetchAllMessages()
      ]);
    }
    if (lastMessageId != null && allMessages.length > 0) {
      const lastMsg = allMessages.find(msg => msg.id === lastMessageId);
      if (lastMsg) {
        updateCurrentMessaged(lastMsg);
      } else {
        console.error('Last message not found in allMessages');
      }
    }
  }, [chatId]);

  const fetchChatDetail = async () => {
    try {
      const detail = await getChatDetail(chatId);
      setChatDetail(detail);
      const lastMessageId = detail.last_message;
      setLastMessageId(lastMessageId);
    } catch (err) {
      console.error('Failed to load chat detail');
    }
  }

  const fetchAllMessages = async () => {
    try {
      const messages = await getAllMessages(chatId);
      setAllMessages(messages);
    } catch (err) {
      console.error('Failed to load all messages');
    }
  }

  const updateCurrentMessaged = (lastMessage: ChatMessage) => {
    const historyIds = [...lastMessage.history, lastMessage.id];
    const messageMap = new Map<number, ChatMessage>(
      allMessages.map(msg => [msg.id, msg])
    );
    const orderedMessages: ChatMessage[] = [];
    for (const id of historyIds) {
      const msg = messageMap.get(id);
      if (msg) {
        orderedMessages.push(msg);
      } else {
        console.warn(`Message with ID ${id} not found in allMessages`);
      }
    }
    setCurrentMessages(orderedMessages);
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !chatId) return;

    const userMsg: ChatMessage = {
      id: -1,
      role: 'user',
      message: inputMessage.trim(),
      media_type: 'text',
      media: '',
      conducted: dayjs(),
      history: [],
    };

    setCurrentMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);
    setError('');

    try {
      const res = await sendChatMessage(chatId, inputMessage.trim(), lastMessageId);
      const userMessage = res.user_message
      const aiMessage = res.ai_message
      setAllMessages((prev) => [...prev, userMessage, aiMessage]);
      setCurrentMessages((prev) =>
        [...prev.filter((msg) => msg.id !== -1), userMessage, aiMessage]
      );
      setLastMessageId(aiMessage.id);
    } catch (err) {
      console.error('Chat error:', err);
      setError('Failed to get response from AI.');
      setAllMessages((prev) => prev.filter((msg) => msg.id !== userMsg.id));
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setError('');
  };

  if (!chatId || isNaN(chatId)) {
    return (
      <Box sx={{ maxWidth: 600, margin: '2rem auto', padding: 2 }}>
        <Alert severity="error">Invalid chat ID.</Alert>
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
          {allMessages.length === 0 ? (
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
            allMessages.map((msg) => (
              <Box
                key={msg.id}
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
                  {msg.message}
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

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ChatBot;