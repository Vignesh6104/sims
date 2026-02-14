import React from 'react';
import { School } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";

const PublicHeader = () => {
    const navigate = useNavigate();

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-white/70 backdrop-blur-md">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link to="/" className="flex items-center gap-2">
                    <div className="p-1.5 bg-blue-600 rounded-lg text-white">
                        <School size={20} />
                    </div>
                    <span className="text-xl font-black text-blue-900 tracking-tighter uppercase">
                        SIMS Academy
                    </span>
                </Link>

                <div className="flex items-center gap-4">
                    <Button variant="ghost" className="hidden sm:inline-flex text-gray-600 font-medium" asChild>
                        <Link to="/about">About Us</Link>
                    </Button>
                    <Button className="bg-blue-600 hover:bg-blue-700 shadow-md h-10 px-6 font-bold" onClick={() => navigate('/login')}>
                        Get Started
                    </Button>
                </div>
            </div>
        </header>
    );
};

export default PublicHeader;
