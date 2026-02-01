import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import { useNavigate } from 'react-router-dom';

const PublicHeader = () => {
    const navigate = useNavigate();

    return (
        <AppBar position="static" color="transparent" elevation={0} sx={{ py: 1, backdropFilter: 'blur(10px)', backgroundColor: 'rgba(255,255,255,0.7)' }}>
            <Container maxWidth="lg">
                <Toolbar disableGutters>
                    <SchoolIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography
                        variant="h6"
                        noWrap
                        component="a"
                        href="/"
                        sx={{
                            mr: 2,
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            letterSpacing: '.1rem',
                            color: 'text.primary',
                            textDecoration: 'none',
                            flexGrow: 1
                        }}
                    >
                        SIMS Academy
                    </Typography>

                    <Button variant="contained" color="primary" onClick={() => navigate('/login')}>
                        Get Started
                    </Button>
                </Toolbar>
            </Container>
        </AppBar>
    );
};

export default PublicHeader;
