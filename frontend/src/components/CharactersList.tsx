import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  Button,
} from '@mui/material';
import { getAllCharacters } from '../api/api';
import { CharacterShort } from '../types/character';

// Helper to truncate text
const truncate = (str: string, maxLength: number): string => {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength).trimEnd() + '…';
};

const CharactersList = () => {
  const [characters, setCharacters] = useState<CharacterShort[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAllCharacters()
      .then(setCharacters)
      .catch((err) => setError('Failed to load characters'))
      .finally(() => setLoading(false));
  }, []);

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
                      minHeight: 48, // ensures consistent card height
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
                  component={Link}
                  to={`/chat/${char.id}`}
                  variant="contained"
                  color="primary"
                  sx={{ mt: 2 }}
                >
                  Chat Now
                </Button>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default CharactersList;