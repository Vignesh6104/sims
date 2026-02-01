import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, CssBaseline } from '@mui/material';
import PublicHeader from './PublicHeader';
import PublicFooter from './PublicFooter';

const PublicLayout = () => {
    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'transparent' }}>
            <CssBaseline />
            <PublicHeader />
            <Box component="main" sx={{ flexGrow: 1 }}>
                <Outlet />
            </Box>
            <PublicFooter />
        </Box>
    );
};

export default PublicLayout;
