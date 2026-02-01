import React from 'react';
import { Box, Typography, Container, Paper, Grid, Avatar, Button } from '@mui/material';
import { School, Info, Public, People, HistoryToggleOff, FitnessCenter, GroupAdd, EmojiEvents } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const AboutUs = () => {
    const navigate = useNavigate();
    return (
        <Box sx={{ py: 8, bgcolor: 'background.default' }}>
            <Container maxWidth="lg">
                <Paper elevation={3} sx={{ p: 4, mb: 4, borderRadius: 2 }}>
                    <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <Avatar sx={{ m: '0 auto', bgcolor: 'primary.main', width: 80, height: 80, mb: 2 }}>
                            <School sx={{ fontSize: 50 }} />
                        </Avatar>
                        <Typography variant="h3" component="h1" fontWeight="bold" color="primary.dark" gutterBottom>
                            Welcome to SIMS Academy
                        </Typography>
                        <Typography variant="h6" color="text.secondary">
                            Empowering Minds, Shaping Futures
                        </Typography>
                        <Button 
                            variant="contained" 
                            size="large" 
                            onClick={() => { console.log('Navigating to /login'); navigate('/login'); }}
                            sx={{ mt: 3, px: 5, py: 1.5, fontSize: '1.1rem' }}
                        >
                            Get Started
                        </Button>
                    </Box>

                    <Grid container spacing={4} sx={{ mb: 4 }}>
                        <Grid item xs={12} md={6}>
                            <Typography variant="h5" fontWeight="bold" color="secondary.main" gutterBottom>
                                Our Vision
                            </Typography>
                            <Typography variant="body1" paragraph>
                                To be a leading educational institution fostering a love for learning, critical thinking, and holistic development in every student. We envision a community where innovation thrives and individuals are prepared to meet the challenges of a dynamic world. Our vision extends beyond academic success, aiming to cultivate responsible global citizens who are adaptable, empathetic, and equipped with the skills to make a meaningful impact in society. We are committed to continuous improvement, embracing new pedagogical approaches and technological advancements to create a dynamic and engaging learning environment.
                            </Typography>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Typography variant="h5" fontWeight="bold" color="secondary.main" gutterBottom>
                                Our Mission
                            </Typography>
                            <Typography variant="body1" paragraph>
                                SIMS Academy is committed to providing an inclusive and stimulating environment that encourages academic excellence, personal growth, and social responsibility. We strive to inspire our students to become lifelong learners and responsible global citizens. Through a balanced curriculum, dedicated faculty, and state-of-the-art facilities, we aim to unlock each student's full potential, nurturing their talents and preparing them for future success in higher education and their chosen careers. Our mission is to instill values of integrity, respect, and perseverance.
                            </Typography>
                        </Grid>
                    </Grid>

                    <Box sx={{ mt: 5 }}>
                        <Typography variant="h4" fontWeight="bold" color="primary.main" sx={{ mb: 3, textAlign: 'center' }}>
                            Why Choose Us?
                        </Typography>
                        <Grid container spacing={4}>
                            <Grid item xs={12} sm={4}>
                                <Box sx={{ textAlign: 'center', p: 2 }}>
                                    <Public color="primary" sx={{ fontSize: 60, mb: 2 }} />
                                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                                        Modern Curriculum
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Our curriculum is designed to meet international standards, integrating technology, critical thinking, and practical skills. We constantly update our programs to remain relevant in a rapidly changing world.
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={12} sm={4}>
                                <Box sx={{ textAlign: 'center', p: 2 }}>
                                    <People color="secondary" sx={{ fontSize: 60, mb: 2 }} />
                                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                                        Experienced Faculty
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        A team of dedicated and highly qualified educators passionate about student success, providing personalized attention and mentorship.
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={12} sm={4}>
                                <Box sx={{ textAlign: 'center', p: 2 }}>
                                    <Info color="success" sx={{ fontSize: 60, mb: 2 }} />
                                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                                        Holistic Development
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Focus on academic, social, emotional, and physical well-being of every student through diverse extracurricular activities and support programs.
                                    </Typography>
                                </Box>
                            </Grid>
                        </Grid>
                    </Box>

                    <Box sx={{ mt: 8 }}>
                        <Typography variant="h4" fontWeight="bold" color="primary.main" sx={{ mb: 3, textAlign: 'center' }}>
                            Our History
                        </Typography>
                        <Grid container spacing={4} alignItems="center">
                            <Grid item xs={12} md={6}>
                                <Avatar sx={{ m: '0 auto', bgcolor: 'info.main', width: 100, height: 100, mb: 2 }}>
                                    <HistoryToggleOff sx={{ fontSize: 60 }} />
                                </Avatar>
                                <Typography variant="h6" fontWeight="bold" gutterBottom align="center">
                                    A Legacy of Excellence
                                </Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Typography variant="body1" paragraph>
                                    Founded in 1995 with a vision to revolutionize education, SIMS Academy has grown from a humble beginning into a beacon of academic and personal achievement. Over the decades, we have consistently adapted to the evolving educational landscape, integrating modern teaching methodologies with timeless values. Our journey is marked by numerous milestones, including national accolades in academics and sports, and a growing alumni network that contributes significantly to various fields worldwide.
                                </Typography>
                                <Typography variant="body1" paragraph>
                                    We pride ourselves on a rich tradition of nurturing talent and fostering a community where every student feels valued and inspired to reach their highest potential. Our commitment to innovation and excellence continues to drive us forward, building upon the strong foundations laid by our founders.
                                </Typography>
                            </Grid>
                        </Grid>
                    </Box>

                    <Box sx={{ mt: 8 }}>
                        <Typography variant="h4" fontWeight="bold" color="primary.main" sx={{ mb: 3, textAlign: 'center' }}>
                            Facilities & Campus Life
                        </Typography>
                        <Grid container spacing={4} alignItems="center">
                            <Grid item xs={12} md={6}>
                                <Typography variant="body1" paragraph>
                                    Our sprawling campus offers state-of-the-art facilities designed to provide a conducive environment for learning and growth. This includes technologically advanced smart classrooms, well-equipped science and computer labs, a vast library with an extensive collection of resources, and dedicated art and music studios. For physical development, we boast expansive sports grounds, indoor recreational areas, and a modern gymnasium.
                                </Typography>
                                <Typography variant="body1" paragraph>
                                    Beyond academics, student life at SIMS Academy is vibrant and engaging. We offer a wide array of extracurricular activities, clubs, and societies, ranging from robotics and debate to drama and environmental conservation. Regular events, workshops, and inter-school competitions ensure a dynamic and enriching experience for all.
                                </Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Avatar sx={{ m: '0 auto', bgcolor: 'warning.main', width: 100, height: 100, mb: 2 }}>
                                    <FitnessCenter sx={{ fontSize: 60 }} />
                                </Avatar>
                                <Typography variant="h6" fontWeight="bold" gutterBottom align="center">
                                    Modern Learning Environment
                                </Typography>
                            </Grid>
                        </Grid>
                    </Box>

                    <Box sx={{ mt: 8 }}>
                        <Typography variant="h4" fontWeight="bold" color="primary.main" sx={{ mb: 3, textAlign: 'center' }}>
                            Student Success & Testimonials
                        </Typography>
                        <Grid container spacing={4} alignItems="center">
                            <Grid item xs={12} md={6}>
                                <Avatar sx={{ m: '0 auto', bgcolor: 'success.main', width: 100, height: 100, mb: 2 }}>
                                    <EmojiEvents sx={{ fontSize: 60 }} />
                                </Avatar>
                                <Typography variant="h6" fontWeight="bold" gutterBottom align="center">
                                    Proud of Our Achievements
                                </Typography>
                                <Typography variant="body1" paragraph>
                                    Our students consistently achieve outstanding results in academic examinations, often topping district and national rankings. Beyond academics, they excel in various extracurricular fields, securing awards in sports, arts, and innovation challenges. Our alumni are testaments to our success, pursuing higher education in prestigious universities worldwide and building successful careers.
                                </Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Typography variant="body1" paragraph>
                                    "SIMS Academy provided me with the perfect foundation for my university studies. The teachers were incredibly supportive, and the diverse curriculum truly broadened my horizons." - **[Student Name], Class of 2020**
                                </Typography>
                                <Typography variant="body1" paragraph>
                                    "The focus on holistic development here is unparalleled. I not only achieved academic excellence but also discovered my passion for robotics, thanks to the amazing clubs and facilities." - **[Student Name], Class of 2022**
                                </Typography>
                            </Grid>
                        </Grid>
                    </Box>


                </Paper>
            </Container>
        </Box>
    );
};

export default AboutUs;
