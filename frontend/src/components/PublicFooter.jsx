import React from 'react';
import { Box, Typography, Container, Link } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';

const PublicFooter = () => {
    return (
        <Box sx={{ bgcolor: 'rgba(255, 255, 255, 0.7)', color: 'text.primary', py: 4, mt: 'auto', mb: 0, backdropFilter: 'blur(10px)' }}>
            <Container maxWidth="lg">
                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: { xs: 2, md: 0 } }}>
                        <SchoolIcon sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant="h6" noWrap>
                            SIMS Academy
                        </Typography>
                    </Box>
                    <Box sx={{ mb: { xs: 2, md: 0 } }}>
                        <Typography variant="body2" color="inherit" align="center">
                            © {new Date().getFullYear()} SIMS Academy. All rights reserved.
                        </Typography>
                    </Box>
                    <Box>
                        <Link href="#" color="inherit" sx={{ mx: 1 }}>Privacy Policy</Link>
                        <Link href="#" color="inherit" sx={{ mx: 1 }}>Terms of Service</Link>
                    </Box>
                </Box>
            </Container>
        </Box>
    );
};

export default PublicFooter;

