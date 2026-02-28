import React from 'react';
import { 
    School, 
    Globe, 
    Users, 
    Lightbulb, 
    History, 
    Trophy, 
    Activity,
    ArrowRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const AboutUs = () => {
    const navigate = useNavigate();
    return (
        <div className="py-12 bg-background min-h-screen">
            <div className="container mx-auto px-4 max-w-6xl">
                <Card className="glass border-none shadow-xl overflow-hidden mb-12">
                    <CardContent className="p-8 sm:p-12 text-center">
                        <div className="inline-flex p-4 rounded-3xl bg-primary text-primary-foreground mb-6 shadow-lg shadow-primary/20">
                            <School size={60} />
                        </div>
                        <h1 className="text-4xl sm:text-5xl font-extrabold text-foreground tracking-tight mb-4 uppercase">
                            Welcome to SIMS Academy
                        </h1>
                        <p className="text-xl text-muted-foreground font-medium mb-8">
                            Empowering Minds, Shaping Futures — Excellence in Education since 1995.
                        </p>
                        <Button 
                            size="lg" 
                            className="h-14 px-10 text-lg bg-primary hover:bg-primary/90 text-primary-foreground rounded-full shadow-lg font-bold"
                            onClick={() => navigate('/login')}
                        >
                            Get Started
                            <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                    </CardContent>
                </Card>

                <div className="grid gap-8 md:grid-cols-2 mb-16">
                    <section className="space-y-4">
                        <h2 className="text-2xl font-bold text-primary flex items-center gap-2">
                            <span className="w-8 h-1 bg-primary rounded-full" />
                            Our Vision
                        </h2>
                        <p className="text-muted-foreground leading-relaxed text-lg italic">
                            "To be a leading educational institution fostering a love for learning, critical thinking, and holistic development in every student."
                        </p>
                        <p className="text-muted-foreground leading-relaxed">
                            We envision a community where innovation thrives and individuals are prepared to meet the challenges of a dynamic world. Our vision extends beyond academic success, aiming to cultivate responsible global citizens who are adaptable, empathetic, and equipped with the skills to make a meaningful impact in society.
                        </p>
                    </section>
                    <section className="space-y-4">
                        <h2 className="text-2xl font-bold text-secondary-foreground flex items-center gap-2">
                            <span className="w-8 h-1 bg-secondary rounded-full" />
                            Our Mission
                        </h2>
                        <p className="text-muted-foreground leading-relaxed">
                            SIMS Academy is committed to providing an inclusive and stimulating environment that encourages academic excellence, personal growth, and social responsibility. We strive to inspire our students to become lifelong learners and responsible global citizens. Through a balanced curriculum, dedicated faculty, and state-of-the-art facilities, we aim to unlock each student's full potential.
                        </p>
                    </section>
                </div>

                <div className="mb-16">
                    <h2 className="text-3xl font-bold text-center text-foreground mb-12 uppercase tracking-tight">Why Choose SIMS?</h2>
                    <div className="grid gap-6 sm:grid-cols-3">
                        {[
                            {
                                icon: <Globe className="text-primary" size={40} />,
                                title: "Modern Curriculum",
                                desc: "Designed to meet international standards, integrating technology, critical thinking, and practical skills for the 21st century."
                            },
                            {
                                icon: <Users className="text-secondary-foreground" size={40} />,
                                title: "Experienced Faculty",
                                desc: "Dedicated educators passionate about student success, providing personalized attention and mentorship to every learner."
                            },
                            {
                                icon: <Lightbulb className="text-primary/70" size={40} />,
                                title: "Holistic Development",
                                desc: "Focus on academic, social, emotional, and physical well-being through diverse extracurricular activities."
                            }
                        ].map((feature, idx) => (
                            <Card key={idx} className="bg-card border border-border/50 shadow-md hover:shadow-lg transition-shadow duration-300">
                                <CardContent className="p-8 text-center space-y-4">
                                    <div className="flex justify-center">{feature.icon}</div>
                                    <h3 className="text-xl font-bold text-foreground">{feature.title}</h3>
                                    <p className="text-sm text-muted-foreground leading-relaxed">{feature.desc}</p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>

                <div className="space-y-16">
                    <section className="flex flex-col md:flex-row items-center gap-12 bg-card p-8 rounded-3xl shadow-sm border border-border/30">
                        <div className="w-full md:w-1/2 order-2 md:order-1 space-y-4">
                            <h3 className="text-2xl font-bold text-foreground flex items-center gap-3">
                                <History className="text-primary" />
                                A Legacy of Excellence
                            </h3>
                            <p className="text-muted-foreground leading-relaxed">
                                Founded in 1995 with a vision to revolutionize education, SIMS Academy has grown from a humble beginning into a beacon of academic achievement. Our journey is marked by numerous milestones, including national accolades and a growing alumni network contributing worldwide.
                            </p>
                        </div>
                        <div className="w-full md:w-1/2 order-1 md:order-2 flex justify-center">
                            <div className="w-48 h-48 bg-primary/10 rounded-full flex items-center justify-center border-4 border-primary/20 shadow-inner">
                                <History size={80} className="text-primary/30" />
                            </div>
                        </div>
                    </section>

                    <section className="flex flex-col md:flex-row items-center gap-12 p-8">
                        <div className="w-full md:w-1/2 flex justify-center">
                            <div className="w-48 h-48 bg-secondary/10 rounded-full flex items-center justify-center border-4 border-secondary/20 shadow-inner">
                                <Activity size={80} className="text-secondary/30" />
                            </div>
                        </div>
                        <div className="w-full md:w-1/2 space-y-4">
                            <h3 className="text-2xl font-bold text-foreground flex items-center gap-3">
                                <Activity className="text-secondary" />
                                Campus Life & Facilities
                            </h3>
                            <p className="text-muted-foreground leading-relaxed">
                                Our sprawling campus offers state-of-the-art facilities: technologically advanced smart classrooms, science and computer labs, and a vast library. We boast expansive sports grounds and dedicated studios for art and music to ensure a vibrant student life.
                            </p>
                        </div>
                    </section>

                    <section className="flex flex-col md:flex-row items-center gap-12 bg-muted/30 p-8 rounded-3xl border border-border/50">
                        <div className="w-full md:w-1/2 order-2 md:order-1 space-y-6">
                            <h3 className="text-2xl font-bold text-foreground flex items-center gap-3">
                                <Trophy className="text-primary" />
                                Student Success
                            </h3>
                            <div className="space-y-4">
                                <blockquote className="border-l-4 border-primary pl-4 italic text-muted-foreground">
                                    "SIMS Academy provided me with the perfect foundation. The teachers were incredibly supportive, and the diverse curriculum truly broadened my horizons."
                                    <footer className="mt-2 font-bold text-foreground">— Sarah J., Class of 2020</footer>
                                </blockquote>
                                <blockquote className="border-l-4 border-primary pl-4 italic text-muted-foreground">
                                    "The focus on holistic development here is unparalleled. I not only achieved academic excellence but also discovered my passion for robotics."
                                    <footer className="mt-2 font-bold text-foreground">— Mark T., Class of 2022</footer>
                                </blockquote>
                            </div>
                        </div>
                        <div className="w-full md:w-1/2 order-1 md:order-2 flex justify-center">
                            <Trophy size={120} className="text-primary/20" />
                        </div>
                    </section>
                </div>
                
                <footer className="mt-20 py-8 border-t border-border/50 text-center text-muted-foreground/60 text-sm">
                    © 2026 SIMS Academy Information Management System. All rights reserved.
                </footer>
            </div>
        </div>
    );
};

export default AboutUs;
