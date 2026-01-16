import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Paper,
} from '@mui/material';
import { useAuth } from '../auth/AuthProvider';
import { SignUpData } from '../auth/types';

const SignUp = () => {
  const [formData, setFormData] = useState<SignUpData>({
    username: '',
    password: '',
    password2: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (error) setError(null); // Clear error on input change
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Client-side validation
    if (formData.password !== formData.password2) {
      setError('Passwords do not match.');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setSubmitting(true);

    try {
      await register(formData);
      // On success, redirect to sign-in (or auto-login if your API supports it)
      navigate('/sign-in', {
        state: { message: 'Account created successfully! Please sign in.' }
      });
    } catch (err: any) {
      console.error('Registration failed:', err);
      setError(
        err.response?.data?.detail ||
        err.response?.data?.username?.[0] ||
        err.response?.data?.password?.[0] ||
        err.message ||
        'Failed to create account. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        maxWidth: 400,
        margin: '2rem auto',
        padding: 3,
      }}
    >
      <Paper elevation={3} sx={{ padding: 3 }}>
        <Typography variant="h5" component="h1" align="center" gutterBottom>
          Create Account
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            margin="normal"
            required
            disabled={submitting}
            autoComplete="username"
          />
          <TextField
            fullWidth
            label="Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            margin="normal"
            required
            disabled={submitting}
            autoComplete="new-password"
          />
          <TextField
            fullWidth
            label="Confirm Password"
            name="password2"
            type="password"
            value={formData.password2}
            onChange={handleChange}
            margin="normal"
            required
            disabled={submitting}
            autoComplete="new-password"
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            disabled={
              submitting ||
              !formData.username ||
              !formData.password ||
              !formData.password2
            }
            sx={{ mt: 2, py: 1 }}
          >
            {submitting ? <CircularProgress size={24} color="inherit" /> : 'Sign Up'}
          </Button>
        </form>

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2">
            Already have an account?{' '}
            <Link to="/sign-in" style={{ textDecoration: 'none' }}>
              Sign In
            </Link>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default SignUp;