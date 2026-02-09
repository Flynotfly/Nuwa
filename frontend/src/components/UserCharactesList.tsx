import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  Button,
  Snackbar,
  IconButton,
  Tooltip,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import ChatIcon from '@mui/icons-material/Chat';
import { getAllCharacters } from '../api/api';
import { createChat } from '../api/api';
import { CharacterShort } from '../types/character';

// Helper to truncate text with ellipsis
const truncateDescription = (str: string, maxLength: number = 120): string => {
  if (!str || str.trim() === '') return 'No description available.';
  if (str.length <= maxLength) return str.trim();
  return str.substring(0, maxLength).trimEnd() + '…';
};

const UserCharactersList = () => {
  const [characters, setCharacters] = useState<CharacterShort[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string }>({
    open: false,
    message: '',
  });
  const navigate = useNavigate();

  useEffect(() => {
    getAllCharacters(true)
      .then(setCharacters)
      .catch(() => setError('Failed to load characters'))
      .finally(() => setLoading(false));
  }, []);

  const handleChatClick = async (characterId: number) => {

    try {
      const chat = await createChat(characterId);
      navigate(`/chat/${chat.id}`);
    } catch (err) {
      console.error('Failed to create chat:', err);
      setSnackbar({ open: true, message: 'Could not start chat. Please try again.' });
    }
  };

  const handleEditClick = (characterId: number) => {
    navigate(`/characters/edit/${characterId}`);
  };

  const handleSnackbarClose = () => setSnackbar({ ...snackbar, open: false });

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress size={48} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ margin: 2, maxWidth: 600, mx: 'auto' }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, margin: '0 auto', padding: { xs: 1, sm: 2 } }}>
      <Typography
        variant="h4"
        align="center"
        gutterBottom
        sx={{
          fontWeight: 600,
          mb: 4,
          background: 'linear-gradient(45deg, #6a11cb 0%, #2575fc 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}
      >
        Your Characters
      </Typography>

      {characters.length === 0 ? (
        <Alert severity="info" sx={{ maxWidth: 600, mx: 'auto' }}>
          You haven't created any characters yet. Create your first character to get started!
        </Alert>
      ) : (
        <Grid container spacing={{ xs: 2, md: 3 }} justifyContent="center">
          {characters.map((char) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={char.id}>
              <Paper
                elevation={4}
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 2,
                  transition: 'transform 0.3s, box-shadow 0.3s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
                  },
                  overflow: 'hidden',
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <Box sx={{ p: 2.5, flexGrow: 1 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      fontWeight: 600,
                      color: 'primary.main',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1
                    }}
                  >
                    {char.name}
                  </Typography>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      minHeight: 60,
                      lineHeight: 1.5,
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {truncateDescription(char.description)}
                  </Typography>
                </Box>

                <Box
                  sx={{
                    p: 2,
                    pt: 1,
                    borderTop: '1px solid',
                    borderColor: 'divider',
                    display: 'flex',
                    gap: 1.5,
                    flexWrap: 'wrap',
                  }}
                >
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={() => handleChatClick(char.id)}
                    startIcon={<ChatIcon />}
                    sx={{
                      textTransform: 'none',
                      fontWeight: 500,
                      py: 1.2,
                      boxShadow: 'none',
                      '&:hover': { boxShadow: '0 4px 12px rgba(37, 117, 252, 0.3)' }
                    }}
                  >
                    Chat
                  </Button>
                  <Button
                    variant="outlined"
                    color="secondary"
                    fullWidth
                    onClick={() => handleEditClick(char.id)}
                    startIcon={<EditIcon />}
                    sx={{
                      textTransform: 'none',
                      fontWeight: 500,
                      py: 1.2,
                      borderColor: 'secondary.light',
                      '&:hover': {
                        borderColor: 'secondary.main',
                        bgcolor: 'action.hover'
                      }
                    }}
                  >
                    Edit
                  </Button>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        message={snackbar.message}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        sx={{ mb: 2 }}
      />
    </Box>
  );
};

export default UserCharactersList;