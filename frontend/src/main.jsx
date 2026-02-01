import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { SnackbarProvider } from 'notistack';
import './global.css';

// Create a professional theme
const theme = createTheme({
  palette: {
    mode: 'light', // Set theme to light mode
    primary: {
      main: '#1976d2', // Standard blue for primary
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#9c27b0', // Standard purple for secondary
      light: '#ba68c8',
      dark: '#7b1fa2',
      contrastText: '#ffffff',
    },
    background: {
      default: 'rgba(255, 255, 255, 0.5)', // Semi-transparent light background
      paper: 'rgba(255, 255, 255, 0.8)', // More opaque white for glass effect
    },
    text: {
      primary: '#212121', // Dark text for light background
      secondary: '#757575', // Medium grey for secondary text
    },
  },
  typography: {
    fontFamily: "'Inter', 'Roboto', 'Arial', sans-serif",
    h1: { fontSize: '2.5rem', fontWeight: 700, letterSpacing: '-0.02em', color: '#212121' },
    h2: { fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.01em', color: '#212121' },
    h3: { fontSize: '1.75rem', fontWeight: 600, color: '#212121' },
    h4: { fontSize: '1.5rem', fontWeight: 600, color: '#212121' },
    h5: { fontSize: '1.25rem', fontWeight: 600, color: '#212121' },
    h6: { fontSize: '1rem', fontWeight: 600, color: '#212121' },
    button: { textTransform: 'none', fontWeight: 500 },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
          },
        },
        contained: {
          background: 'linear-gradient(145deg, rgba(25, 118, 210, 0.8), rgba(25, 118, 210, 0.6))',
          color: '#ffffff',
          '&:hover': {
            background: 'linear-gradient(145deg, rgba(25, 118, 210, 0.9), rgba(25, 118, 210, 0.7))',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          },
        }
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: 'none',
          backgroundImage: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          boxShadow: 'none',
        },
        elevation1: {
          boxShadow: 'none',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(0, 0, 0, 0.05)', // Light border for light theme
        },
        head: {
          backgroundColor: 'rgba(0, 0, 0, 0.03)', // Subtle background for header
          color: '#212121', // Dark text for header
          fontWeight: 600,
        },
      },
    },
    MuiInputBase: { // Adjust input fields for glassmorphism
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(255, 255, 255, 0.8)', // Opaque white
          borderRadius: 8,
          border: '1px solid rgba(0, 0, 0, 0.1)', // Subtle dark border for input base
          '&:hover fieldset': {
            borderColor: 'rgba(0, 0, 0, 0.2) !important',
          },
          '&.Mui-focused fieldset': {
            borderColor: '#1976d2 !important', // Primary color for focused
          },
        },
        input: {
          color: '#212121', // Dark text for inputs
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: 'rgba(0, 0, 0, 0.6)', // Softer dark label color
          '&.Mui-focused': {
            color: '#1976d2', // Primary color for focused label
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        notchedOutline: {
          borderColor: 'transparent', // Border handled by MuiInputBase-root
        },
      },
    },
    MuiCssBaseline: {
      styleOverrides: `
        .MuiInputLabel-root.Mui-focused {
          color: #000000 !important;
        }
      `,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        <BrowserRouter>
          <AuthProvider>
            <App />
          </AuthProvider>
        </BrowserRouter>
      </SnackbarProvider>
    </ThemeProvider>
  </React.StrictMode>,
)