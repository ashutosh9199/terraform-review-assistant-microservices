import { createTheme } from '@mui/material/styles';
import type {} from '@mui/x-data-grid/themeAugmentation';

const border = '#e1e7f0';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#205493',
      dark: '#133a65',
      light: '#4d79b3'
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
      default: '#f5f7fb',
      paper: '#ffffff'
    },
    text: {
      primary: '#172033',
      secondary: '#536176'
    },
    divider: border
  },
  typography: {
    fontFamily: 'Inter, Arial, sans-serif',
    h3: { fontWeight: 700, letterSpacing: '-0.02em' },
    h4: { fontWeight: 700, letterSpacing: '-0.01em' },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
    overline: { fontWeight: 700, letterSpacing: '0.08em' },
    button: { textTransform: 'none', fontWeight: 600 }
  },
  shape: {
    borderRadius: 10
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '::-webkit-scrollbar': { width: 10, height: 10 },
        '::-webkit-scrollbar-thumb': { backgroundColor: '#c3cee0', borderRadius: 8 },
        '::-webkit-scrollbar-track': { backgroundColor: 'transparent' }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          borderRadius: 8
        },
        sizeLarge: {
          paddingTop: 10,
          paddingBottom: 10,
          paddingLeft: 22,
          paddingRight: 22
        },
        containedPrimary: {
          backgroundImage: 'linear-gradient(135deg, #205493 0%, #163d6e 100%)',
          '&:hover': {
            backgroundImage: 'linear-gradient(135deg, #1c4a83 0%, #133a65 100%)',
            boxShadow: '0 6px 16px rgba(32, 84, 147, 0.28)'
          }
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: `1px solid ${border}`,
          borderRadius: 12,
          boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04), 0 1px 14px rgba(16, 24, 40, 0.03)'
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none'
        },
        elevation0: {
          border: `1px solid ${border}`
        }
      }
    },
    MuiAppBar: {
      styleOverrides: {
        colorInherit: {
          backgroundColor: '#ffffff'
        }
      }
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600
        }
      }
    },
    MuiTextField: {
      defaultProps: {
        size: 'small'
      }
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 8
        }
      }
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8
        }
      }
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: 'none',
          '--DataGrid-rowBorderColor': border
        },
        columnHeaders: {
          backgroundColor: '#f5f7fb',
          borderBottom: `1px solid ${border}`
        },
        columnHeaderTitle: {
          fontWeight: 700
        }
      }
    }
  }
});
