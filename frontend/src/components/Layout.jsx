import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    AppBar,
    Box,
    CssBaseline,
    Drawer,
    IconButton,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Typography,
    Avatar,
    Menu,
    MenuItem,
    Tooltip,
    Divider,
    useMediaQuery,
    useTheme
} from '@mui/material';
import {
    Menu as MenuIcon,
    Dashboard as DashboardIcon,
    People as PeopleIcon,
    Group as GroupIcon,
    School as SchoolIcon,
    Class as ClassIcon,
    Book as BookIcon,
    Assignment as AssignmentIcon,
    Logout as LogoutIcon,
    EventNote as EventNoteIcon,
    BarChart as BarChartIcon,
    Notifications as NotificationsIcon,
    CalendarMonth as CalendarIcon,
    LocalLibrary as LibraryIcon
} from '@mui/icons-material';

const drawerWidth = 240;

const Layout = () => {
    const { user, role, logout } = useAuth();
    const [mobileOpen, setMobileOpen] = useState(false);
    const [anchorElUser, setAnchorElUser] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    // Close mobile drawer on navigation
    useEffect(() => {
        setMobileOpen(false);
    }, [location]);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const handleOpenUserMenu = (event) => {
        setAnchorElUser(event.currentTarget);
    };

    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };

    const handleLogout = () => {
        handleCloseUserMenu();
        logout();
    };

    const menuItems = {
        admin: [
            { text: 'Dashboard', icon: <DashboardIcon />, path: '/admin' },
            { text: 'Admins', icon: <GroupIcon />, path: '/admin/admins' },
            { text: 'Teachers', icon: <PeopleIcon />, path: '/admin/teachers' },
            { text: 'Students', icon: <SchoolIcon />, path: '/admin/students' },
            { text: 'Classes', icon: <ClassIcon />, path: '/admin/classes' },
            { text: 'Subjects', icon: <BookIcon />, path: '/admin/subjects' },
            { text: 'Exams', icon: <AssignmentIcon />, path: '/admin/exams' },
            { text: 'Timetable', icon: <EventNoteIcon />, path: '/admin/timetable' },
            { text: 'Calendar', icon: <CalendarIcon />, path: '/admin/calendar' },
            { text: 'Library', icon: <LibraryIcon />, path: '/admin/library' },
            { text: 'Fees', icon: <BarChartIcon />, path: '/admin/fees' },
            { text: 'Notifications', icon: <NotificationsIcon />, path: '/admin/notifications' },
        ],
        teacher: [
            { text: 'Dashboard', icon: <DashboardIcon />, path: '/teacher' },
            { text: 'Attendance', icon: <EventNoteIcon />, path: '/teacher/attendance' },
            { text: 'Marks', icon: <BarChartIcon />, path: '/teacher/marks' },
            { text: 'Assignments', icon: <AssignmentIcon />, path: '/teacher/assignments' },
            { text: 'Calendar', icon: <CalendarIcon />, path: '/teacher/calendar' },
            { text: 'Library', icon: <LibraryIcon />, path: '/teacher/library' },
            { text: 'Notifications', icon: <NotificationsIcon />, path: '/teacher/notifications' },
        ],
        student: [
            { text: 'Dashboard', icon: <DashboardIcon />, path: '/student' },
            { text: 'Attendance', icon: <EventNoteIcon />, path: '/student/attendance' },
            { text: 'Marks', icon: <BarChartIcon />, path: '/student/marks' },
            { text: 'Assignments', icon: <AssignmentIcon />, path: '/student/assignments' },
            { text: 'Calendar', icon: <CalendarIcon />, path: '/student/calendar' },
            { text: 'Library', icon: <LibraryIcon />, path: '/student/library' },
            { text: 'Notifications', icon: <NotificationsIcon />, path: '/student/notifications' },
        ],
        parent: [
            { text: 'Dashboard', icon: <DashboardIcon />, path: '/parent' },
            { text: 'Calendar', icon: <CalendarIcon />, path: '/parent/calendar' },
            { text: 'Notifications', icon: <NotificationsIcon />, path: '/parent/notifications' },
        ],
    };

    const drawer = (
        <div>
            <Box sx={{ 
                p: 4, 
                textAlign: 'center', 
                background: 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)', 
                color: 'white',
                borderBottomLeftRadius: 24,
                borderBottomRightRadius: 24,
                mb: 2,
                mx: 1,
                mt: 1,
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}>
                <Avatar 
                    sx={{ 
                        width: 72, 
                        height: 72, 
                        margin: '0 auto 16px',
                        bgcolor: 'rgba(255,255,255,0.2)',
                        color: 'white',
                        fontSize: '1.75rem',
                        fontWeight: 'bold',
                        border: '2px solid rgba(255,255,255,0.3)'
                    }}
                >
                    {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </Avatar>
                <Typography variant="h6" fontWeight="bold">
                    {user?.full_name}
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.8, textTransform: 'uppercase', letterSpacing: 1 }}>
                    {role}
                </Typography>
            </Box>
            <List sx={{ px: 2 }}>
                {(menuItems[role] || []).map((item) => (
                    <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
                        <ListItemButton 
                            selected={location.pathname === item.path}
                            onClick={() => navigate(item.path)}
                            sx={{
                                borderRadius: 3,
                                '&.Mui-selected': {
                                    backgroundColor: 'primary.light',
                                    color: 'white',
                                    '&:hover': {
                                        backgroundColor: 'primary.main',
                                    },
                                    '& .MuiListItemIcon-root': {
                                        color: 'white',
                                    }
                                },
                                '&:hover': {
                                    backgroundColor: 'action.hover',
                                },
                            }}
                        >
                            <ListItemIcon sx={{ minWidth: 40, color: location.pathname === item.path ? 'inherit' : 'text.secondary' }}>
                                {item.icon}
                            </ListItemIcon>
                            <ListItemText primary={item.text} primaryTypographyProps={{ fontWeight: 500 }} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
        </div>
    );

    return (
        <Box sx={{ display: 'flex', background: 'transparent' }}>
            <CssBaseline />
            <AppBar
                position="fixed"
                sx={{
                    width: { sm: `calc(100% - ${drawerWidth}px)` },
                    ml: { sm: `${drawerWidth}px` },
                    bgcolor: 'rgba(255, 255, 255, 0.7)', // Glassmorphism effect for light theme
                    color: 'text.primary',
                    boxShadow: '0 4px 30px rgba(0, 0, 0, 0.1)',
                    backdropFilter: 'blur(10px)',
                    borderBottom: '1px solid rgba(0, 0, 0, 0.1)'
                }}
            >
                <Toolbar>
                    <IconButton
                        color="inherit"
                        aria-label="open drawer"
                        edge="start"
                        onClick={handleDrawerToggle}
                        sx={{ mr: 2, display: { sm: 'none' } }}
                    >
                        <MenuIcon />
                    </IconButton>
                    <Box sx={{ flexGrow: 1 }} />
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Tooltip title="Notifications">
                            <IconButton 
                                color="inherit" 
                                sx={{ mr: 2 }}
                                onClick={() => navigate(`/${role}/notifications`)}
                            >
                                <NotificationsIcon />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Open settings">
                            <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                                <Avatar sx={{ bgcolor: 'secondary.main' }}>
                                    {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                                </Avatar>
                            </IconButton>
                        </Tooltip>
                        <Menu
                            sx={{ mt: '45px' }}
                            id="menu-appbar"
                            anchorEl={anchorElUser}
                            anchorOrigin={{
                                vertical: 'top',
                                horizontal: 'right',
                            }}
                            keepMounted
                            transformOrigin={{
                                vertical: 'top',
                                horizontal: 'right',
                            }}
                            open={Boolean(anchorElUser)}
                            onClose={handleCloseUserMenu}
                        >
                            <MenuItem onClick={handleCloseUserMenu}>
                                <Typography textAlign="center">Profile</Typography>
                            </MenuItem>
                            <MenuItem onClick={handleLogout}>
                                <ListItemIcon>
                                    <LogoutIcon fontSize="small" />
                                </ListItemIcon>
                                <Typography textAlign="center">Logout</Typography>
                            </MenuItem>
                        </Menu>
                    </Box>
                </Toolbar>
            </AppBar>
            <Box
                component="nav"
                sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
                aria-label="mailbox folders"
            >
                {isMobile ? (
                    <Drawer
                        variant="temporary"
                        open={mobileOpen}
                        onClose={handleDrawerToggle}
                        ModalProps={{
                            keepMounted: true, // Better open performance on mobile.
                            disableEnforceFocus: true,
                            disableAutoFocus: true
                        }}
                        sx={{
                            display: { xs: 'block', sm: 'none' },
                            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                        }}
                    >
                        {drawer}
                    </Drawer>
                ) : (
                    <Drawer
                        variant="permanent"
                        sx={{
                            display: { xs: 'none', sm: 'block' },
                            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                        }}
                        open
                    >
                        {drawer}
                    </Drawer>
                )}
            </Box>
            <Box
                component="main"
                sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` }, mt: 8 }}
            >
                <Outlet />
            </Box>
        </Box>
    );
};

export default Layout;
