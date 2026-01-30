import React, { useEffect, useState, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Snackbar,
  IconButton,
  Tooltip,
  Grid,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  Delete as DeleteIcon,
  ArrowBack as BackIcon,
} from '@mui/icons-material';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import {
  createCharacter,
  getCharacterById,
  updateCharacter,
  destroyCharacter,
} from '../api/api';
import { CharacterFull, NewCharacterFull } from '../types/character';

// Initial form state constant
const INITIAL_FORM_STATE: NewCharacterFull = {
  name: '',
  description: '',
  system_prompt: '',
  is_private: false,
  is_hidden_prompt: false,
};

const CharacterFormPage = () => {
  const { id } = useParams<{ id?: string }>();
  const isEditMode = !!id;
  const navigate = useNavigate();
  const location = useLocation();

  // Form state
  const [formData, setFormData] = useState<NewCharacterFull>(INITIAL_FORM_STATE);

  // UI state
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteConfirmationText, setDeleteConfirmationText] = useState('');
  const [ownershipVerified, setOwnershipVerified] = useState(true);

  // Track previous ID to detect route changes within same component
  const prevIdRef = useRef<string | undefined>(undefined);

  // CRITICAL FIX: Reset form when route changes (edit → create or edit → edit different ID)
  useEffect(() => {
    // Detect when we transition between routes using the same component
    const prevId = prevIdRef.current;
    const currentId = id;

    // Reset form if:
    // 1. Going from edit mode to create mode (id existed → now undefined)
    // 2. Going from one edit page to another (different IDs)
    if ((prevId && !currentId) || (prevId && currentId && prevId !== currentId)) {
      setFormData(INITIAL_FORM_STATE);
      setFormError(null);
    }

    // Also load character data if in edit mode with a valid ID
    if (isEditMode && id) {
      setLoading(true);
      getCharacterById(Number(id))
        .then((data) => {
          setFormData({
            name: data.name,
            description: data.description,
            system_prompt: data.system_prompt,
            is_private: data.is_private,
            is_hidden_prompt: data.is_hidden_prompt,
          });
          setLoading(false);
        })
        .catch(() => {
          setFormError('Failed to load character details. Please try again.');
          setLoading(false);
        });
    }

    // Update ref for next render
    prevIdRef.current = id;
  }, [id, isEditMode]); // Dependencies ensure this runs on route param changes

  // Handle input changes
  const handleChange = (
    field: keyof NewCharacterFull
  ) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: field.includes('is_') ? event.target.checked : event.target.value,
    }));
    setFormError(null);
  };

  // Form validation
  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setFormError('Character name is required');
      return false;
    }
    if (formData.name.trim().length < 2) {
      setFormError('Character name must be at least 2 characters');
      return false;
    }
    if (!formData.system_prompt.trim()) {
      setFormError('System prompt is required for character behavior');
      return false;
    }
    if (formData.system_prompt.trim().length < 10) {
      setFormError('System prompt should be at least 10 characters');
      return false;
    }
    return true;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    try {
      if (isEditMode && id) {
        await updateCharacter(Number(id), formData);
        showSnackbar('Character updated successfully!', 'success');
      } else {
        const newChar = await createCharacter(formData);
        showSnackbar('Character created successfully!', 'success');
        setTimeout(() => navigate(`/characters/edit/${newChar.id}`), 1000);
      }
    } catch (err) {
      console.error('Save failed:', err);
      showSnackbar(
        isEditMode
          ? 'Failed to update character. Please check your inputs.'
          : 'Failed to create character. Name might be taken.',
        'error'
      );
    } finally {
      setLoading(false);
    }
  };

  // Delete handling
  const handleDeleteClick = () => {
    setDeleteConfirmationText('');
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    // Critical validation: must match exactly (case-sensitive)
    if (deleteConfirmationText.trim() !== formData.name.trim()) {
      setFormError('Character name does not match. Deletion cancelled.');
      return;
    }

    if (!isEditMode || !id) return;

    setLoading(true);
    try {
      await destroyCharacter(Number(id));
      showSnackbar('Character permanently deleted', 'success');
      setTimeout(() => navigate('/my-characters'), 1000);
    } catch (err) {
      console.error('Delete failed:', err);
      showSnackbar('Failed to delete character. It might be in use.', 'error');
    } finally {
      setLoading(false);
      setDeleteDialogOpen(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDeleteConfirmationText('');
  };

  // Utility functions
  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  };
  const handleSnackbarClose = () => setSnackbar(prev => ({ ...prev, open: false }));
  const handleBack = () => navigate('/my-characters');

  // Loading state for initial data fetch
  if (loading && isEditMode) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="70vh">
        <CircularProgress size={48} />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, margin: '0 auto', px: 2, py: 3 }}>
      <Paper elevation={3} sx={{ p: { xs: 2, sm: 3 }, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <IconButton onClick={handleBack} sx={{ mr: 1.5 }}>
            <BackIcon />
          </IconButton>
          <Typography variant="h5" fontWeight={600}>
            {isEditMode ? 'Edit Character' : 'Create New Character'}
          </Typography>
        </Box>

        {formError && (
          <Alert severity="error" sx={{ mb: 2.5 }} onClose={() => setFormError(null)}>
            {formError}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={2.5}>
            {/* Name Field */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Character Name *"
                value={formData.name}
                onChange={handleChange('name')}
                error={!!formError && !formData.name.trim()}
                helperText={
                  !formData.name.trim() && formError
                    ? 'Required field'
                    : 'How users will identify this character'
                }
                inputProps={{ maxLength: 50 }}
                disabled={loading}
                required
              />
            </Grid>

            {/* Description Field */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Public Description"
                multiline
                rows={2}
                value={formData.description}
                onChange={handleChange('description')}
                helperText="Brief description shown to users (optional)"
                inputProps={{ maxLength: 300 }}
                disabled={loading}
              />
            </Grid>

            {/* System Prompt Field - ALWAYS VISIBLE */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" fontWeight={500} sx={{ mb: 1 }}>
                System Prompt *
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={8}
                value={formData.system_prompt}
                onChange={handleChange('system_prompt')}
                error={!!formError && !formData.system_prompt.trim()}
                helperText={
                  formData.system_prompt.trim().length < 10 && formData.system_prompt.trim()
                    ? 'Should be at least 10 characters'
                    : 'Core instructions defining character personality and behavior (only visible to you)'
                }
                inputProps={{ maxLength: 2000 }}
                disabled={loading}
                required
                sx={{
                  fontFamily: 'monospace',
                  fontSize: '0.92rem',
                }}
              />
            </Grid>

            {/* Privacy Controls */}
            <Grid item xs={12}>
              <Divider sx={{ my: 1.5 }} />
              <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_private}
                      onChange={handleChange('is_private')}
                      disabled={loading}
                      color="primary"
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body1" fontWeight={500}>
                        Private Character
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Only visible to you in your character list
                      </Typography>
                    </Box>
                  }
                  sx={{ flex: 1 }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_hidden_prompt}
                      onChange={handleChange('is_hidden_prompt')}
                      disabled={loading}
                      color="secondary"
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body1" fontWeight={500}>
                        Hide Prompt in UI
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Prevent accidental exposure during screen sharing (applies outside this form)
                      </Typography>
                    </Box>
                  }
                  sx={{ flex: 1 }}
                />
              </Box>
            </Grid>

            {/* Action Buttons */}
            <Grid item xs={12}>
              <Box sx={{
                display: 'flex',
                flexDirection: { xs: 'column', sm: 'row' },
                gap: 1.5,
                mt: 1
              }}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  startIcon={<SaveIcon />}
                  disabled={loading}
                  fullWidth
                  sx={{
                    py: 1.5,
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: 'none',
                    '&:hover': { boxShadow: '0 4px 12px rgba(37, 117, 252, 0.3)' }
                  }}
                >
                  {loading ? (
                    <CircularProgress size={24} sx={{ color: 'white' }} />
                  ) : isEditMode ? (
                    'Update Character'
                  ) : (
                    'Create Character'
                  )}
                </Button>

                {isEditMode && (
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<DeleteIcon />}
                    onClick={handleDeleteClick}
                    disabled={loading}
                    fullWidth
                    sx={{
                      py: 1.5,
                      fontWeight: 600,
                      textTransform: 'none',
                      color: 'error.main',
                      borderColor: 'error.main',
                      '&:hover': {
                        borderColor: 'error.dark',
                        bgcolor: 'error.lighter'
                      }
                    }}
                  >
                    Delete Character
                  </Button>
                )}
              </Box>

              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ display: 'block', mt: 1.5, textAlign: 'center' }}
              >
                * Required fields • System prompt defines core character behavior
              </Typography>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ fontWeight: 600, color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Confirm Character Deletion
        </DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>
            Are you sure you want to permanently delete <strong>"{formData.name}"</strong>?
          </Typography>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This action cannot be undone. All associated chat history will be preserved but
            cannot be continued with this character.
          </Alert>
          <Typography sx={{ mb: 1 }}>
            Type the character's name below to confirm deletion:
          </Typography>
          <TextField
            fullWidth
            margin="dense"
            value={deleteConfirmationText}
            onChange={(e) => setDeleteConfirmationText(e.target.value)}
            error={deleteConfirmationText.trim() !== formData.name.trim()}
            helperText={
              deleteConfirmationText.trim() !== formData.name.trim()
                ? `Must exactly match: "${formData.name}"`
                : 'Name matches - confirmation valid'
            }
            placeholder={`Type "${formData.name}" exactly`}
            autoFocus
          />
        </DialogContent>
        <DialogActions sx={{ p: 2.5 }}>
          <Button
            onClick={handleDeleteCancel}
            disabled={loading}
            sx={{ fontWeight: 500 }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            variant="contained"
            color="error"
            startIcon={loading ? <CircularProgress size={20} /> : <DeleteIcon />}
            disabled={
              loading ||
              deleteConfirmationText.trim() !== formData.name.trim()
            }
            sx={{ fontWeight: 600, px: 3 }}
          >
            {loading ? 'Deleting...' : 'Permanently Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar Notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        sx={{ mb: 8 }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          sx={{
            width: '100%',
            borderRadius: 2,
            fontWeight: 500,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            '& .MuiAlert-icon': { fontSize: 24 }
          }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CharacterFormPage;