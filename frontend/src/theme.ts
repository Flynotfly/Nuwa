import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Example: matches MUI default blue, but you can change
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#fff',
    },
    secondary: {
      main: '#ff4081', // Pink accent — matches "Get Started Free" button
      dark: '#c60055',
      contrastText: '#fff',
    },
    background: {
      default: '#f5f7fa', // Light gray — like your features section
      paper: '#ffffff',
    },
    text: {
      primary: '#333333',
      secondary: '#666666',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

export default theme;