import React from 'react';
import ChatBot from './components/ChatBot';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2', // You can customize this
        },
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <ChatBot />
        </ThemeProvider>
    );
}

export default App;