import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { AlertCircle, Home } from 'lucide-react';

const NotFound = () => {
    const navigate = useNavigate();

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-blue-600 text-white p-4">
            <AlertCircle size={120} className="mb-8 opacity-20" />
            <h1 className="text-9xl font-black tracking-tighter mb-4">404</h1>
            <h2 className="text-2xl font-bold mb-8 text-center max-w-md">
                The page you’re looking for doesn’t exist or has been moved.
            </h2>
            <Button
                size="lg"
                onClick={() => navigate('/')}
                className="bg-white text-blue-600 hover:bg-gray-100 font-bold h-12 px-8 rounded-full shadow-xl"
            >
                <Home className="mr-2 h-5 w-5" />
                Return to Safety
            </Button>
        </div>
    );
};

export default NotFound;
