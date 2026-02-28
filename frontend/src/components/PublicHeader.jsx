import React from 'react';
import { School, Sun, Moon, Palette } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { useTheme } from '../context/ThemeContext';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

const PublicHeader = () => {
    const navigate = useNavigate();
    const { theme, toggleTheme } = useTheme();

    return (
        <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/70 backdrop-blur-md">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link to="/" className="flex items-center gap-2">
                    <div className="p-1.5 bg-primary rounded-lg text-primary-foreground">
                        <School size={20} />
                    </div>
                    <span className="text-xl font-black text-foreground tracking-tighter uppercase">
                        SIMS Academy
                    </span>
                </Link>

                <div className="flex items-center gap-2 sm:gap-4">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={toggleTheme}
                                    className="text-foreground"
                                >
                                    {theme === 'default' ? <Sun size={20} /> : theme === 'midnight' ? <Moon size={20} /> : <Palette size={20} />}
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>Switch Theme</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>

                    <Button variant="ghost" className="hidden sm:inline-flex text-muted-foreground font-medium" asChild>
                        <Link to="/about">About Us</Link>
                    </Button>
                    <Button className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-md h-10 px-6 font-bold" onClick={() => navigate('/login')}>
                        Get Started
                    </Button>
                </div>
            </div>
        </header>
    );
};

export default PublicHeader;
