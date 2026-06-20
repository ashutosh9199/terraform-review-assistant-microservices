import {
  Assessment as AssessmentIcon,
  CloudUpload as CloudUploadIcon,
  Dashboard as DashboardIcon,
  Layers as LayersIcon,
  Logout as LogoutIcon,
  ManageSearch as ManageSearchIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Typography
} from '@mui/material';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { clearToken, getCurrentUserEmail } from '../api/client';
import { LlmOnboardingModal } from './LlmOnboardingModal';

const drawerWidth = 268;

const navItems = [
  { label: 'Dashboard', path: '/app', icon: <DashboardIcon fontSize="small" /> },
  { label: 'Upload', path: '/app/upload', icon: <CloudUploadIcon fontSize="small" /> },
  { label: 'Analysis', path: '/app/reports', icon: <ManageSearchIcon fontSize="small" /> },
  { label: 'Reports', path: '/app/reports', icon: <AssessmentIcon fontSize="small" /> },
  { label: 'Settings', path: '/app/settings', icon: <SettingsIcon fontSize="small" /> }
];

function BrandMark() {
  return (
    <Stack direction="row" alignItems="center" spacing={1.25}>
      <Box
        sx={{
          width: 34,
          height: 34,
          borderRadius: 2,
          display: 'grid',
          placeItems: 'center',
          backgroundImage: 'linear-gradient(135deg, #205493 0%, #133a65 100%)',
          color: '#fff',
          flexShrink: 0
        }}
      >
        <LayersIcon fontSize="small" />
      </Box>
      <Box>
        <Typography variant="subtitle1" sx={{ lineHeight: 1.1 }}>
          Terraform Review
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1 }}>
          Assistant
        </Typography>
      </Box>
    </Stack>
  );
}

export function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const email = getCurrentUserEmail() ?? 'signed in';
  const initials = email
    .split('@')[0]
    .split(/[._-]/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('') || 'U';

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <LlmOnboardingModal />
      <AppBar
        position="fixed"
        color="inherit"
        elevation={0}
        sx={{ borderBottom: '1px solid', borderColor: 'divider', zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar sx={{ gap: 2 }}>
          <Box sx={{ flex: 1 }} />
          <Button
            color="inherit"
            startIcon={<LogoutIcon />}
            onClick={() => {
              clearToken();
              navigate('/login');
            }}
          >
            Sign out
          </Button>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: 'border-box',
            borderRight: '1px solid',
            borderColor: 'divider',
            display: 'flex'
          }
        }}
      >
        <Box sx={{ height: 64, display: 'flex', alignItems: 'center', px: 2.5 }}>
          <BrandMark />
        </Box>
        <Divider />
        <Box sx={{ px: 2.5, pt: 2, pb: 1 }}>
          <Typography variant="overline" color="text.secondary">
            Review Workspace
          </Typography>
        </Box>
        <List sx={{ px: 1.5, flex: 1 }}>
          {navItems.map((item) => {
            const selected = location.pathname === item.path;
            return (
              <ListItemButton
                key={item.path + item.label}
                selected={selected}
                onClick={() => navigate(item.path)}
                sx={{
                  mb: 0.5,
                  borderLeft: '3px solid',
                  borderColor: selected ? 'primary.main' : 'transparent',
                  '&.Mui-selected': {
                    bgcolor: 'rgba(32, 84, 147, 0.08)'
                  },
                  '&.Mui-selected:hover': {
                    bgcolor: 'rgba(32, 84, 147, 0.12)'
                  }
                }}
              >
                <ListItemIcon sx={{ minWidth: 36, color: selected ? 'primary.main' : 'text.secondary' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{ fontWeight: selected ? 600 : 500, color: selected ? 'text.primary' : 'text.secondary' }}
                />
              </ListItemButton>
            );
          })}
        </List>
        <Divider />
        <Stack direction="row" spacing={1.5} alignItems="center" sx={{ p: 2 }}>
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main', fontSize: 14 }}>{initials}</Avatar>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="body2" fontWeight={600} noWrap>
              {email.split('@')[0]}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {email}
            </Typography>
          </Box>
        </Stack>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, pt: 11 }}>
        <Outlet />
      </Box>
    </Box>
  );
}
