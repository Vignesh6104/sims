import React from 'react';
import { School } from 'lucide-react';
import { Link } from 'react-router-dom';

const PublicFooter = () => {
    return (
        <footer className="w-full border-t bg-white/70 backdrop-blur-md py-12">
            <div className="container mx-auto px-4">
                <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="flex items-center gap-2">
                        <div className="p-1.5 bg-blue-600 rounded-lg text-white">
                            <School size={20} />
                        </div>
                        <span className="text-xl font-black text-blue-900 tracking-tighter uppercase">
                            SIMS Academy
                        </span>
                    </div>
                    
                    <p className="text-sm text-muted-foreground font-medium order-3 md:order-2">
                        © {new Date().getFullYear()} SIMS Academy. All rights reserved.
                    </p>
                    
                    <div className="flex items-center gap-6 order-2 md:order-3">
                        <Link href="#" className="text-sm font-semibold text-gray-500 hover:text-blue-600 transition-colors">Privacy Policy</Link>
                        <Link href="#" className="text-sm font-semibold text-gray-500 hover:text-blue-600 transition-colors">Terms of Service</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default PublicFooter;
