import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#205493',
      dark: '#133a65'
    },
    secondary: {
      main: '#1f7a6d'
    },
    error: {
      main: '#b42318'
    },
    warning: {
      main: '#b54708'
    },
    success: {
      main: '#027a48'
    },
    background: {
      default: '#f6f8fb',
      paper: '#ffffff'
    },
    text: {
      primary: '#172033',
      secondary: '#536176'
    }
  },
  typography: {
    fontFamily: 'Inter, Arial, sans-serif',
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 600 }
  },
  shape: {
    borderRadius: 8
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          boxShadow: 'none'
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: '1px solid #d9e1ec',
          boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04)'
        }
      }
    }
  }
});
