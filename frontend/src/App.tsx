import Router from './Router'
import { AuthProvider } from './auth/AuthProvider'
import theme from "./theme";
import {CssBaseline, ThemeProvider} from "@mui/material";


function App() {

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <AuthProvider>
                <Router />
            </AuthProvider>
        </ThemeProvider>
    )
}

export default App
