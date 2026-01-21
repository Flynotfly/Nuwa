import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 👈 Add this
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  Button,
  Snackbar,
} from '@mui/material';
import { getAllCharacters } from '../api/api';
import { createChat } from '../api/api'; //
import { CharacterShort } from '../types/character';
import { useAuth } from '../auth/AuthProvider'; //

// Helper to truncate text
const truncate = (str: string, maxLength: number): string => {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength).trimEnd() + '…';
};

const CharactersList = () => {
  const [characters, setCharacters] = useState<CharacterShort[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    getAllCharacters()
      .then(setCharacters)
      .catch((err) => setError('Failed to load characters'))
      .finally(() => setLoading(false));
  }, []);

  const handleChatClick = async (characterId: number) => {
    if (!isAuthenticated) {
      setSnackbarOpen(true);
      return;
    }

    try {
      const chat = await createChat(characterId);
      navigate(`/chat/${chat.id}`);
    } catch (err) {
      console.error('Failed to create chat:', err);
      setError('Could not start chat. Please try again.');
    }
  };

  const handleSnackbarClose = () => setSnackbarOpen(false);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" mt={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ margin: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ maxWidth: 900, margin: '0 auto', padding: 2 }}>
      <Typography variant="h4" align="center" gutterBottom>
        Choose Your AI Companion
      </Typography>

      {characters.length === 0 ? (
        <Alert severity="info">No characters available.</Alert>
      ) : (
        <Grid container spacing={2} justifyContent="center">
          {characters.map((char) => (
            <Grid item xs={12} sm={6} md={4} key={char.id}>
              <Paper
                elevation={3}
                sx={{
                  padding: 2,
                  textAlign: 'center',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <Box>
                  <Typography variant="h6" gutterBottom>
                    {char.name}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      minHeight: 48,
                      overflow: 'hidden',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {char.description && char.description.trim() !== ''
                      ? truncate(char.description, 100)
                      : 'No description available.'}
                  </Typography>
                </Box>
                <Button
                  variant="contained"
                  color="primary"
                  sx={{ mt: 2 }}
                  onClick={() => handleChatClick(char.id)} // 👈 Not a Link!
                >
                  Chat Now
                </Button>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
        message="Please log in to start a chat."
      />
    </Box>
  );
};

export default CharactersList;