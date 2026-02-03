import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import { getAllChats } from '../api/api';
import { ChatListElement } from '../types/chat';
import { useAuth } from '../auth/AuthProvider';
import dayjs, { Dayjs } from "dayjs";

// Format datetime to show relative time for today, otherwise date + time
const formatChatTime = (date: Dayjs): string => {
  const now = dayjs();
  if (date.isSame(now, 'day')) {
    return date.format('HH:mm');
  }
  if (date.isSame(now, 'year')) {
    return date.format('MMM D, HH:mm');
  }
  return date.format('MMM D, YYYY, HH:mm');
};

const ChatsList = () => {
  const [chats, setChats] = useState<ChatListElement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    getAllChats()
      .then(setChats)
      .catch((err) => {
        console.error('Failed to load chats:', err);
        setError(err.response?.status === 401
          ? 'Session expired. Please log in again.'
          : 'Failed to load chats. Please try again later.');
      })
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  const handleChatClick = (chatId: number) => {
    navigate(`/chat/${chatId}`);
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="70vh"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ maxWidth: 900, margin: '0 auto', padding: 2 }}>
        <Alert
          severity={error.includes('log in') ? 'warning' : 'error'}
          sx={{
            margin: 2,
            justifyContent: 'center',
            '& .MuiAlert-message': { width: '100%', textAlign: 'center' }
          }}
        >
          {error}
        </Alert>
        {error.includes('log in') && (
          <Box display="flex" justifyContent="center" mt={2}>
            <Button
              variant="contained"
              color="primary"
              onClick={() => navigate('/login')}
            >
              Go to Login
            </Button>
          </Box>
        )}
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 900, margin: '0 auto', padding: 2 }}>
      <Typography variant="h4" align="center" gutterBottom sx={{ mb: 4 }}>
        Your Conversations
      </Typography>

      {chats.length === 0 ? (
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            textAlign: 'center',
            backgroundColor: 'background.default'
          }}
        >
          <Typography variant="h6" gutterBottom>
            No active conversations yet
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Start a new chat from the Characters page to see it here
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/')}
          >
            Browse Characters
          </Button>
        </Paper>
      ) : (
        <Box display="flex" flexDirection="column" gap={2}>
          {chats.map((chat) => (
            <Paper
              key={chat.id}
              elevation={3}
              sx={{
                padding: 2.5,
                cursor: 'pointer',
                transition: 'box-shadow 0.3s, transform 0.2s',
                '&:hover': {
                  boxShadow: 6,
                  transform: 'translateY(-2px)',
                },
                backgroundColor: 'background.paper',
                borderLeft: '4px solid',
                borderColor: 'primary.main',
              }}
              onClick={() => handleChatClick(chat.id)}
            >
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                <Typography variant="h6" fontWeight="600">
                  {chat.character_name}
                </Typography>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{
                    whiteSpace: 'nowrap',
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                    px: 1,
                    py: 0.5,
                    borderRadius: 1
                  }}
                >
                  {formatChatTime(chat.last_message_datetime)}
                </Typography>
              </Box>
              <Typography
                variant="body1"
                color="text.secondary"
                sx={{
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  minHeight: '2.4em'
                }}
              >
                {chat.last_message_text || 'No messages yet'}
              </Typography>
            </Paper>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default ChatsList;