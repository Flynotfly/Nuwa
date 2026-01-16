import React, { useState } from 'react';
import {
  Outlet,
  Link,
  useLocation,
  useNavigate,
} from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Divider,
  Button,
  useTheme,
  useMediaQuery,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Person as PersonIcon,
  Chat as ChatIcon,
  Favorite as FavoriteIcon,
  Login as LoginIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useAuth } from '../auth/AuthProvider';

// Define tab routes
const publicTabs = [
  { label: 'Characters', icon: <PersonIcon />, path: '/' },
  { label: 'Chats', icon: <ChatIcon />, path: '/chats' },
];

const privateTabs = [
  { label: 'My Characters', icon: <FavoriteIcon />, path: '/my-characters' },
];

const Layout = () => {
  const { user, logout, loading: authLoading } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/sign-in');
  };

  // Determine active tab by matching path prefix
  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  // Combine tabs based on auth state
  const allTabs = [...publicTabs, ...(user?.isAuthenticated ? privateTabs : [])];

  // Auth buttons
  const renderAuthButtons = () => (
    <Box sx={{ p: 2, pt: 1 }}>
      {!user?.isAuthenticated ? (
        <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 1 }}>
          <Button
            component={Link}
            to="/sign-in"
            startIcon={<LoginIcon />}
            size="small"
            fullWidth={isMobile}
          >
            Sign In
          </Button>
          <Button
            component={Link}
            to="/sign-up"
            variant="contained"
            color="primary"
            size="small"
            fullWidth={isMobile}
          >
            Sign Up
          </Button>
        </Box>
      ) : (
        <Button
          onClick={handleLogout}
          startIcon={<LogoutIcon />}
          color="error"
          size="small"
          fullWidth
          sx={{ justifyContent: 'flex-start' }}
        >
          Logout ({user.username})
        </Button>
      )}
    </Box>
  );

  // Drawer content
  const drawer = (
    <Box
      sx={{
        width: 250,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          AI Companions
        </Typography>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1, py: 1 }}>
        {allTabs.map((tab) => (
          <ListItem
            button
            key={tab.path}
            component={Link}
            to={tab.path}
            selected={isActive(tab.path)}
            onClick={isMobile ? () => setMobileOpen(false) : undefined}
            sx={{
              borderRadius: 1,
              mb: 0.5,
              '&.Mui-selected': {
                backgroundColor: 'primary.light',
                color: 'primary.contrastText',
                '& .MuiListItemIcon-root': {
                  color: 'primary.contrastText',
                },
              },
            }}
          >
            <ListItemIcon>{tab.icon}</ListItemIcon>
            <ListItemText primary={tab.label} />
          </ListItem>
        ))}
      </List>
      <Box sx={{ flexGrow: 1 }} />
      {renderAuthButtons()}
    </Box>
  );

  if (authLoading) {
    return (
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <AppBar position="fixed">
          <Toolbar>
            <Typography variant="h6">AI Companions</Typography>
          </Toolbar>
        </AppBar>
        <Box component="main" sx={{ flexGrow: 1, mt: 8, p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
        }}
      >
        {drawer}
      </Drawer>

      {/* Permanent drawer on desktop */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
        }}
        open
      >
        {drawer}
      </Drawer>

      {/* Main content */}
      <Box component="main" sx={{ flexGrow: 1, bgcolor: 'background.default' }}>
        <AppBar
          position="fixed"
          sx={{
            ml: { sm: 250 },
            width: { sm: `calc(100% - 250px)` },
            zIndex: theme.zIndex.drawer + 1,
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div">
              {location.pathname === '/'
                ? 'Characters'
                : location.pathname.startsWith('/chat')
                  ? 'Chat'
                  : allTabs.find((t) => location.pathname.startsWith(t.path))?.label ||
                  'AI Companions'}
            </Typography>
          </Toolbar>
        </AppBar>
        <Toolbar /> {/* Spacer for fixed app bar */}
        <Box sx={{ p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;