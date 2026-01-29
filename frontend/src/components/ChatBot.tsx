// components/ChatBot.tsx
import React, { useState, useEffect, useRef } from 'react';
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
  IconButton,
  Link,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from '@mui/icons-material/Send';
import ImageIcon from '@mui/icons-material/Image';
import DownloadIcon from '@mui/icons-material/Download';
import dayjs from 'dayjs';
import { useParams } from 'react-router-dom';
import { getChatDetail, getAllMessages, sendChatMessage } from '../api/api';
import { ChatMessage } from '../types/chatting';
import { ChatDetail } from '../types/chat';
import { updateChatStructure, removeLastElementIfNotEmpty, findBranches, rebaseBranch } from '../utils';

const ChatBot = () => {
  const { id } = useParams<{ id: string }>();
  const chatId = Number(id);

  const mediaBaseURL = import.meta.env.VITE_BASE_URL;

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  type ChatStructure = (number | ChatStructure)[];

  const [chatDetail, setChatDetail] = useState<ChatDetail | null>(null);
  const [allMessages, setAllMessages] = useState<ChatMessage[]>([]);
  const [lastMessageId, setLastMessageId] = useState<number | null>(null);
  const [chatStructure, setChatStructure] = useState<ChatStructure>([]);
  const [branchesChoices, setBranchesChoices] = useState<number[]>([]);
  const [chosenBranches, setChosenBranches] = useState<number[]>([]);
  const [currentMessages, setCurrentMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [editingMessageId, setEditingMessageId] = useState<number | null>(null);
  const [editMessageText, setEditMessageText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPrompt, setShowPrompt] = useState(false);

  const formRef = React.useRef<HTMLFormElement>(null);
  const imageLoadStatus = useRef<Record<string, boolean>>({});

  useEffect(() => {
    if (!chatId || isNaN(chatId)) {
      setError('Invalid chat ID.');
      return;
    }
    const loadAll = async () => {
      try {
        const [detail, messages] = await Promise.all([
          getChatDetail(chatId),
          getAllMessages(chatId)
        ]);
        setChatDetail(detail);
        setLastMessageId(detail.last_message);
        setChatStructure(detail.structure);
        setAllMessages(messages);
        if (detail.last_message != null && messages.length > 0) {
          const lastMsg = messages.find(msg => msg.id === detail.last_message);
          if (lastMsg) {
            updateCurrentMessages(lastMsg, messages, detail.structure);
          } else {
            console.error('Last message not found in allMessages');
          }
        }
      } catch (err) {
        console.error('Failed to load chat or messages:', err);
        setError('Failed to load chat data.');
      } finally {
        setLoading(false);
      }
    }
    loadAll();
  }, [chatId]);

  // Update current messages from all messages using last message
  const updateCurrentMessages = (
    lastMessage: ChatMessage,
    messages: ChatMessage[],
    structure: ChatStructure
  ) => {
    const historyIds = [...lastMessage.history, lastMessage.id];
    const messageMap = new Map<number, ChatMessage>(
      messages.map(msg => [msg.id, msg])
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
    const [newBranchesChoices, choices] = findBranches(structure, lastMessage.id, lastMessage.history);
    setBranchesChoices(newBranchesChoices);
    setChosenBranches(choices);
  }

  const handleChangeBranch = (msg: ChatMessage, index: number, direction: number) => {
    if (loading) return;
    const newBranch = chosenBranches[index] + direction;
    const newMessagesIds = rebaseBranch(chatStructure, msg.history, newBranch);
    const messageMap = new Map(allMessages.map(m => [m.id, m]));
    const newMessages = newMessagesIds
      .map(id => messageMap.get(id))
      .filter((msg): msg is ChatMessage => msg !== undefined);
    setCurrentMessages(newMessages);
    const lastMessage = newMessages[newMessages.length - 1];
    if (lastMessage) {
      setLastMessageId(lastMessage.id);
      const [newBranchesChoices, choices] = findBranches(chatStructure, lastMessage.id, lastMessage.history);
      setBranchesChoices(newBranchesChoices);
      setChosenBranches(choices);
    }

  };

  const resolveMediaUrl = (mediaPath: string): string => {
    if (!mediaPath || typeof mediaPath !== 'string') return '';
    if (
      mediaPath.startsWith('http://') ||
      mediaPath.startsWith('https://') ||
      mediaPath.startsWith('data:')
    ) {
      return mediaPath;
    }
    if (!mediaBaseURL) {
      console.warn('VITE_BASE_URL not configured! Using raw media path:', mediaPath);
      return mediaPath;
    }
    // Normalize: remove trailing slashes from base, leading slashes from path
    const baseUrl = mediaBaseURL.trim().replace(/\/+$/, '');
    const path = mediaPath.trim().replace(/^\/+/, '');
    return path ? `${baseUrl}/${path}` : baseUrl;
  };

  const handleEditMessage = (msg: ChatMessage) => {
    setEditingMessageId(msg.id);
    setEditMessageText(msg.message);
  };

  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditMessageText('');
  };

  const handleImageError = (msgId: number, src: string) => {
    console.error(`Failed to load image for message ${msgId} with source ${src}`);
  };

  const handleSaveEdit = async (msg: ChatMessage) => {
    if (!editMessageText.trim() || !chatId) return;

    console.log('Save edit for message ID:', msg.id, 'New text:', editMessageText);
    setEditingMessageId(null);
    setEditMessageText('');
    const index = currentMessages.findIndex(m => m.id === msg.id);
    if (index === -1) {
      console.warn('Message not found in currentMessages for forking');
      return;
    }
    const newCurrentMessages = currentMessages.slice(0, index + 1);
    const prevMessageId = newCurrentMessages.length > 1
      ? newCurrentMessages[newCurrentMessages.length - 2].id
      : null;
    setCurrentMessages(newCurrentMessages);
    setBranchesChoices(prev => prev.slice(0, index + 1));
    setChosenBranches(prev => prev.slice(0, index + 1));
    const lastKeptMessage = newCurrentMessages[newCurrentMessages.length - 1];
    setLastMessageId(lastKeptMessage.id);
    setBranchesChoices(prev => {
      const truncated = prev.slice(0, index + 1);
      truncated[truncated.length - 1] += 1;
      return truncated;
    });
    setChosenBranches(prev => {
      const truncated = prev.slice(0, index + 1);
      truncated[truncated.length - 1] += 1;
      return truncated;
    });
    setCurrentMessages(prev =>
      prev.map(m =>
        m.id === msg.id ? {
          id: -1,
          role: 'user',
          message: editMessageText.trim(),
          media_type: 'text',
          media: '',
          conducted: dayjs(),
          history: [],
        } : m
      )
    );
    await sendMessage(true, prevMessageId, false);
  };

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

    await sendMessage(false, lastMessageId, false);
  };

  const handleGenerateImage = async () => {
    if (!chatId) return;
    setInputMessage('');
    await sendMessage(false, lastMessageId, true);
  }

  const sendMessage = async (isEdit: boolean, _lastMessageId: number, is_gen_image: boolean) => {
    setLoading(true);
    setError('');
    try {
      const sendPreviousMessageId = _lastMessageId;
      const messageToSend = isEdit ? editMessageText.trim() : inputMessage.trim();
      const res = await sendChatMessage(chatId, messageToSend, sendPreviousMessageId, is_gen_image);
      const newMessages = res.messages;
      if (!Array.isArray(newMessages) || newMessages.length === 0) {
        console.error("Received empty messages array from API");
        return;
      }
      console.log('New messages: ', newMessages);
      setAllMessages((prev) => [...prev, ...newMessages]);
      setCurrentMessages((prev) =>
        [...prev.filter((msg) => msg.id !== -1), ...newMessages]
      );
      setLastMessageId(newMessages[newMessages.length - 1].id);
      let updatedStructure = chatStructure;
      let currentParentId = sendPreviousMessageId;
      for (const msg of newMessages) {
        updatedStructure = updateChatStructure(
          updatedStructure,
          currentParentId,
          msg.id,
          removeLastElementIfNotEmpty(msg.history),
        )
        currentParentId = msg.id;
      }
      setChatStructure(updatedStructure);
      setBranchesChoices((prev) => [...prev, ...Array(newMessages.length).fill(1)]);
      setChosenBranches((prev) => [...prev, ...Array(newMessages.length).fill(0)]);
    } catch (err) {
      console.error('Chat error:', err);
      setCurrentMessages((prev) => prev.filter((msg) => msg.id !== -1));
      setError('Failed to get response from AI.');
    } finally {
      setLoading(false);
    }
  }

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
          {currentMessages.length === 0 ? (
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
            currentMessages.map((msg, idx) => {
              // Handle potential array length mismatches per requirements
              const totalBranches = idx < branchesChoices.length
                ? branchesChoices[idx]
                : 1;
              const currentBranch = idx < chosenBranches.length
                ? chosenBranches[idx]
                : 0;

              const isEditing = editingMessageId === msg.id;
              const isImageMessage = msg.media_type === 'image' && msg.media;

              return (
                <Box
                  key={msg.id}
                  sx={{
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: isImageMessage ? '90%' : '85%',
                    position: 'relative',
                  }}
                >
                  {isEditing && msg.role === 'user' ? (
                    // Edit mode for user messages
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 1,
                        width: '100%',
                      }}
                    >
                      <TextField
                        fullWidth
                        multiline
                        maxRows={4}
                        value={editMessageText}
                        onChange={(e) => setEditMessageText(e.target.value)}
                        variant="outlined"
                        size="small"
                        autoFocus
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                          },
                        }}
                      />
                      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                        <Button
                          size="small"
                          onClick={handleCancelEdit}
                          disabled={loading}
                          sx={{ borderRadius: 1 }}
                        >
                          Cancel
                        </Button>
                        <Button
                          size="small"
                          variant="contained"
                          onClick={() => handleSaveEdit(msg)}
                          disabled={loading || !editMessageText.trim()}
                          sx={{ borderRadius: 1 }}
                          endIcon={<SendIcon />}
                        >
                          Save
                        </Button>
                      </Box>
                    </Box>
                  ) : (
                    // Normal message display
                    <>
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
                          padding: isImageMessage ? 1 : 1.5,
                          borderRadius: 2,
                          borderTopLeftRadius: msg.role === 'user' ? 2 : 0,
                          borderTopRightRadius: msg.role === 'user' ? 0 : 2,
                          wordBreak: 'break-word',
                          whiteSpace: 'pre-wrap',
                          position: 'relative',
                          maxWidth: '100%',
                        }}
                      >
                        {isImageMessage ? (
                          <Box sx={{ textAlign: 'center' }}>
                            <img
                              src={resolveMediaUrl(msg.media)}
                              alt={msg.message || 'Generated image'}
                              style={{
                                maxWidth: '100%',
                                borderRadius: '8px',
                                display: 'block',
                                margin: '0 auto',
                                maxHeight: '400px',
                                objectFit: 'contain',
                              }}
                              onError={() => handleImageError(msg.id, resolveMediaUrl(msg.media))}
                            />
                            {msg.message && (
                              <Typography
                                variant="caption"
                                display="block"
                                sx={{
                                  mt: 1,
                                  fontStyle: 'italic',
                                  color: msg.role === 'user'
                                    ? 'rgba(255,255,255,0.9)'
                                    : 'text.secondary'
                                }}
                              >
                                {msg.message}
                              </Typography>
                            )}
                            <Link
                              href={resolveMediaUrl(msg.media)}
                              download
                              sx={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                mt: 1,
                                color: msg.role === 'user'
                                  ? theme.palette.primary.contrastText
                                  : theme.palette.primary.main,
                                textDecoration: 'none',
                                '&:hover': { textDecoration: 'underline' },
                              }}
                            >
                              <ImageIcon sx={{ fontSize: 16, mr: 0.5 }} />
                              View full image
                            </Link>
                          </Box>
                        ) : (
                          <Typography variant="body2">
                            {msg.message}
                          </Typography>
                        )}
                      </Box>

                      {/* Edit button - only for text user messages */}
                      {msg.role === 'user' &&
                        msg.id !== -1 &&
                        !isImageMessage && (
                          <IconButton
                            size="small"
                            onClick={() => handleEditMessage(msg)}
                            sx={{
                              mt: 0.5,
                              alignSelf: 'flex-end',
                              color: theme.palette.text.secondary,
                              opacity: 0.7,
                              '&:hover': {
                                opacity: 1,
                                backgroundColor: 'transparent',
                                color: theme.palette.primary.main,
                              },
                              padding: '4px',
                            }}
                            aria-label={`Edit message ${msg.id}`}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        )}

                      {/* Branch navigation - unchanged */}
                      {totalBranches > 1 && (
                        <Box
                          sx={{
                            display: 'flex',
                            justifyContent: 'center',
                            marginTop: 0.75,
                            gap: 0.5,
                            '& .MuiIconButton-root': {
                              width: 28,
                              height: 28,
                              padding: 0.25,
                            }
                          }}
                        >
                          <IconButton
                            size="small"
                            onClick={() => handleChangeBranch(msg, idx, -1)}
                            disabled={currentBranch === 0}
                            aria-label="Previous branch"
                          >
                            <Typography variant="caption" sx={{ fontWeight: 600 }}>&lt;</Typography>
                          </IconButton>

                          <Typography
                            variant="caption"
                            sx={{
                              alignSelf: 'center',
                              minWidth: 40,
                              textAlign: 'center',
                              color: 'text.secondary',
                              fontWeight: 500
                            }}
                          >
                            {currentBranch + 1} / {totalBranches}
                          </Typography>

                          <IconButton
                            size="small"
                            onClick={() => handleChangeBranch(msg, idx, 1)}
                            disabled={currentBranch === totalBranches - 1}
                            aria-label="Next branch"
                          >
                            <Typography variant="caption" sx={{ fontWeight: 600 }}>&gt;</Typography>
                          </IconButton>
                        </Box>
                      )}
                    </>
                    )}
                </Box>
              );
          })
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
          ref={formRef}
          onSubmit={handleSubmit}
          sx={{
            padding: 2,
            borderTop: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.background.paper,
          }}
        >
          <Box sx={{ display: 'flex', gap: 1.5, flexWrap: isMobile ? 'wrap' : 'nowrap' }}>
            <TextField
              fullWidth
              variant="outlined"
              size="small"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={`Message ${chatDetail.character_name}... (Type prompt for image generation)`}
              disabled={loading}
              multiline
              maxRows={3}
              onKeyDown={(event) => {
                if (event.key !== 'Enter') return;
                if (event.ctrlKey || event.metaKey) {
                  event.preventDefault();
                  setInputMessage(prev => prev + '\n');
                  return;
                }
                event.preventDefault();
                formRef.current?.requestSubmit();
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
                flex: 1,
              }}
            />

            {/* Generate Image Button */}
            <Button
              type="button"
              variant="outlined"
              onClick={handleGenerateImage}
              disabled={loading}
              sx={{
                borderRadius: 2,
                minWidth: { xs: 'auto', sm: 140 },
                padding: '8px 16px',
                whiteSpace: 'nowrap',
                height: 'fit-content',
                alignSelf: 'flex-end',
              }}
              startIcon={<ImageIcon />}
            >
              {isMobile ? 'Generate' : 'Generate Image'}
            </Button>

            {/* Send Message Button */}
            <Button
              type="submit"
              variant="contained"
              disabled={loading || !inputMessage.trim()}
              sx={{
                borderRadius: 2,
                minWidth: { xs: 'auto', sm: 120 },
                padding: '8px 16px',
                whiteSpace: 'nowrap',
                height: 'fit-content',
                alignSelf: 'flex-end',
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