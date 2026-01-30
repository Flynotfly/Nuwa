import React, { useState, useMemo, useEffect } from 'react';
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
  CssBaseline,
  Avatar,
  Chip,
  Tooltip,
  Fade,
  Badge,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Person as PersonIcon,
  Chat as ChatIcon,
  Favorite as FavoriteIcon,
  Login as LoginIcon,
  Logout as LogoutIcon,
  AddCircleOutline as AddIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { useAuth } from '../auth/AuthProvider';

// Define navigation items with better organization
const navigationConfig = {
  public: [
    {
      label: 'Characters',
      icon: <PersonIcon />,
      path: '/',
      description: 'Browse available AI companions'
    },
    {
      label: 'Chats',
      icon: <ChatIcon />,
      path: '/chats',
      description: 'View your conversations'
    },
  ],
  private: [
    {
      label: 'My Characters',
      icon: <FavoriteIcon />,
      path: '/my-characters',
      description: 'Manage your custom characters'
    },
    {
      label: 'Create Character',
      icon: <AddIcon />,
      path: '/characters/new',
      description: 'Design your own AI companion',
      variant: 'primary'
    },
  ],
  settings: [
    {
      label: 'Settings',
      icon: <SettingsIcon />,
      path: '/settings',
      description: 'Account and preferences'
    },
  ]
};

const Layout = () => {
  const { user, logout, loading: authLoading } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [contentReady, setContentReady] = useState(false);
  const [notificationCount] = useState(0); // Placeholder for future notifications

  // Memoize navigation items to prevent unnecessary re-renders
  const navigationItems = useMemo(() => {
    const items = [...navigationConfig.public];

    if (user?.isAuthenticated) {
      items.push(...navigationConfig.private);
    }

    items.push(...navigationConfig.settings);

    return items;
  }, [user?.isAuthenticated]);

  useEffect(() => {
    // Small delay to ensure DOM is ready before showing content
    const timer = setTimeout(() => setContentReady(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/sign-in', { replace: true });
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Determine active tab with better matching logic
  const getActiveTab = () => {
    const currentPath = location.pathname;

    // Exact match for home
    if (currentPath === '/') return '/';

    // Find best match
    const activeItem = navigationItems.find(item =>
      currentPath.startsWith(item.path) &&
      currentPath.length >= item.path.length
    );

    return activeItem?.path || '';
  };

  const activeTab = getActiveTab();

  // User avatar with fallback
  const renderUserAvatar = () => {
    if (!user?.isAuthenticated) return null;

    const username = user.username || 'User';
    const initials = username
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);

    return (
      <Tooltip title={username} arrow>
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: 'primary.main',
            fontSize: '0.875rem',
            cursor: 'pointer'
          }}
          onClick={() => navigate('/profile')}
        >
          {initials}
        </Avatar>
      </Tooltip>
    );
  };

  // Enhanced auth section with better UX
  const renderAuthSection = () => (
    <Box
      sx={{
        p: 2,
        pt: 1,
        borderTop: `1px solid ${theme.palette.divider}`,
        backgroundColor: 'background.paper'
      }}
    >
      {!user?.isAuthenticated ? (
        <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 1 }}>
          <Button
            component={Link}
            to="/sign-in"
            startIcon={<LoginIcon />}
            size="medium"
            fullWidth={isMobile}
            variant="outlined"
            sx={{
              borderColor: 'primary.main',
              color: 'primary.main',
              '&:hover': {
                backgroundColor: 'primary.lighter',
                borderColor: 'primary.dark',
              }
            }}
          >
            Sign In
          </Button>
          <Button
            component={Link}
            to="/sign-up"
            variant="contained"
            color="primary"
            size="medium"
            fullWidth={isMobile}
            sx={{
              fontWeight: 600,
              '&:hover': {
                boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
              }
            }}
          >
            Sign Up
          </Button>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            {renderUserAvatar()}
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography
                variant="subtitle2"
                noWrap
                sx={{
                  fontWeight: 600,
                  color: 'text.primary'
                }}
              >
                {user.username}
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                noWrap
              >
                {user.email}
              </Typography>
            </Box>
          </Box>
          <Button
            onClick={handleLogout}
            startIcon={<LogoutIcon />}
            color="error"
            size="medium"
            fullWidth
            variant="outlined"
            sx={{
              justifyContent: 'flex-start',
              borderColor: 'error.main',
              '&:hover': {
                backgroundColor: 'error.lighter',
              }
            }}
          >
            Logout
          </Button>
        </Box>
      )}
    </Box>
  );

  // Enhanced drawer with better visual hierarchy
  const drawerContent = (
    <Box
      sx={{
        width: 280,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'background.default',
      }}
    >
      {/* Header with branding */}
      <Box sx={{ p: 2, pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '50%',
              backgroundColor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'primary.contrastText',
              fontWeight: 700,
              fontSize: '1.25rem',
            }}
          >
            AI
          </Box>
          <Box>
            <Typography
              variant="h6"
              noWrap
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              AI Companions
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              noWrap
            >
              Your AI conversation hub
            </Typography>
          </Box>
        </Box>
      </Box>

      <Divider sx={{ mb: 1 }} />

      {/* Navigation */}
      <List sx={{ px: 1.5, py: 1, flexGrow: 1 }}>
        {navigationItems.map((item) => {
          const isActive = activeTab === item.path;
          const isPrimary = item.variant === 'primary';

          return (
            <Tooltip
              title={item.description}
              arrow
              placement="right"
              key={item.path}
            >
              <ListItem
                button
                component={Link}
                to={item.path}
                selected={isActive}
                onClick={isMobile ? () => setMobileOpen(false) : undefined}
                sx={{
                  borderRadius: 2,
                  mb: 0.75,
                  px: 2,
                  py: 1.25,
                  transition: 'all 0.2s ease',
                  backgroundColor: isActive
                    ? (isPrimary ? 'primary.main' : 'primary.light')
                    : 'transparent',
                  color: isActive
                    ? (isPrimary ? 'primary.contrastText' : 'primary.contrastText')
                    : 'text.primary',
                  '&:hover': {
                    backgroundColor: isPrimary
                      ? 'primary.dark'
                      : 'action.hover',
                    transform: 'translateX(4px)',
                  },
                  '& .MuiListItemIcon-root': {
                    color: isActive
                      ? (isPrimary ? 'primary.contrastText' : 'primary.contrastText')
                      : 'text.secondary',
                    minWidth: 40,
                  },
                  '& .MuiListItemText-primary': {
                    fontWeight: isActive ? 600 : 500,
                  },
                }}
              >
                <ListItemIcon>
                  {React.cloneElement(item.icon as React.ReactElement, {
                    sx: { fontSize: 20 }
                  })}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    variant: 'subtitle1'
                  }}
                />
                {isPrimary && (
                  <Chip
                    label="New"
                    size="small"
                    color="secondary"
                    sx={{
                      height: 20,
                      fontSize: '0.65rem',
                      fontWeight: 700
                    }}
                  />
                )}
              </ListItem>
            </Tooltip>
          );
        })}
      </List>

      {/* Bottom section with auth and notifications */}
      <Box sx={{ p: 1.5 }}>
        <Box sx={{ display: 'flex', gap: 1, mb: 1.5 }}>
          <Tooltip title="Notifications" arrow>
            <Badge badgeContent={notificationCount} color="error">
              <IconButton
                size="small"
                sx={{
                  color: 'text.secondary',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                    color: 'primary.main',
                  }
                }}
              >
                <NotificationsIcon />
              </IconButton>
            </Badge>
          </Tooltip>
        </Box>
        <Divider />
      </Box>

      {renderAuthSection()}
    </Box>
  );

  // Loading state with better UX
  if (authLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          minHeight: '100vh',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: 'background.default'
        }}
      >
        <CssBaseline />
        <Box sx={{ textAlign: 'center' }}>
          <Box
            sx={{
              width: 60,
              height: 60,
              borderRadius: '50%',
              backgroundColor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2,
              animation: 'pulse 1.5s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { transform: 'scale(1)' },
                '50%': { transform: 'scale(1.1)' },
              },
            }}
          >
            <Typography
              variant="h5"
              sx={{
                color: 'primary.contrastText',
                fontWeight: 700
              }}
            >
              AI
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Loading your experience...
          </Typography>
        </Box>
      </Box>
    );
  }

  // Page title based on route
  const getPageTitle = () => {
    if (location.pathname === '/') return 'Characters';
    if (location.pathname.startsWith('/chat')) return 'Chat';
    if (location.pathname.startsWith('/chats')) return 'Your Conversations';
    if (location.pathname.startsWith('/my-characters')) return 'My Characters';
    if (location.pathname.startsWith('/characters/new')) return 'Create Character';
    if (location.pathname.startsWith('/characters/edit')) return 'Edit Character';
    if (location.pathname.startsWith('/settings')) return 'Settings';

    const currentItem = navigationItems.find(item =>
      location.pathname.startsWith(item.path)
    );
    return currentItem?.label || 'AI Companions';
  };

  const pageTitle = getPageTitle();

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />

      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280,
            backgroundColor: 'background.default',
          },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Permanent drawer on desktop - FIXED */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          width: 280,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280,
            position: 'fixed',
            height: '100vh',
            overflowY: 'auto',
            backgroundColor: 'background.default',
            borderRight: 'none',
            boxShadow: '2px 0 8px rgba(0,0,0,0.08)',
          },
        }}
        open
      >
        {drawerContent}
      </Drawer>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          width: { sm: `calc(100% - 280px)` },
          ml: { sm: '280px' },
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* App Bar with gradient */}
        <AppBar
          position="fixed"
          sx={{
            width: { sm: `calc(100% - 280px)` },
            ml: { sm: '280px' },
            zIndex: theme.zIndex.drawer + 1,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
            borderBottom: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          <Toolbar sx={{ minHeight: 64 }}>
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{
                mr: 2,
                display: { sm: 'none' },
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                }
              }}
            >
              <MenuIcon />
            </IconButton>

            <Box sx={{ flex: 1 }}>
              <Fade in={contentReady} timeout={300}>
                <Typography
                  variant="h6"
                  noWrap
                  sx={{
                    fontWeight: 600,
                    letterSpacing: '0.5px'
                  }}
                >
                  {pageTitle}
                </Typography>
              </Fade>
            </Box>

            {/* Desktop user info */}
            <Box sx={{ display: { xs: 'none', sm: 'flex' }, alignItems: 'center', gap: 1.5 }}>
              {notificationCount > 0 && (
                <Tooltip title="Notifications" arrow>
                  <Badge badgeContent={notificationCount} color="error">
                    <IconButton color="inherit" size="small">
                      <NotificationsIcon />
                    </IconButton>
                  </Badge>
                </Tooltip>
              )}
              {renderUserAvatar()}
            </Box>
          </Toolbar>
        </AppBar>

        {/* Spacer for fixed app bar */}
        <Toolbar sx={{ minHeight: 64 }} />

        {/* Main content area - FIXED: Wrapped Outlet in Box for proper DOM node */}
        <Box
          sx={{
            flexGrow: 1,
            p: { xs: 2, sm: 3 },
            overflow: 'auto',
          }}
        >
          {/* CRITICAL FIX: Wrap Outlet in Box to provide DOM node for transitions */}
          <Fade in={contentReady} timeout={400}>
            <Box sx={{ width: '100%' }}>
              <Outlet />
            </Box>
          </Fade>
        </Box>

        {/* Footer */}
        <Box
          component="footer"
          sx={{
            p: 2,
            textAlign: 'center',
            backgroundColor: 'background.paper',
            borderTop: `1px solid ${theme.palette.divider}`,
            fontSize: '0.875rem',
            color: 'text.secondary',
          }}
        >
          <Typography variant="caption">
            © {new Date().getFullYear()} AI Companions. All rights reserved.
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;