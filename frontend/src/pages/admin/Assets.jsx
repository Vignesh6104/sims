import React, { useState, useEffect } from 'react';
import {
    Plus,
    RefreshCw,
    Package,
    MapPin,
    AlertTriangle
} from 'lucide-react';
import api from '../../api/axios';
import { useToast } from "@/components/ui/use-toast";
import { DataTable } from "@/components/ui/data-table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

const Assets = () => {
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();

    const fetchAssets = async () => {
        setLoading(true);
        try {
            const response = await api.get('/assets/');
            setAssets(response.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch assets",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAssets();
    }, []);

    const columns = [
        { accessorKey: "name", header: "Item Name" },
        { accessorKey: "category", header: "Category" },
        { accessorKey: "quantity", header: "Qty" },
        { accessorKey: "location", header: "Location" },
        { 
            accessorKey: "status", 
            header: "Condition",
            cell: ({ row }) => (
                <Badge variant={row.original.status === 'Functional' ? 'outline' : 'destructive'}>
                    {row.original.status}
                </Badge>
            )
        },
        { 
            accessorKey: "purchase_date", 
            header: "Purchase Date",
            cell: ({ row }) => row.original.purchase_date ? format(new Date(row.original.purchase_date), 'PP') : 'N/A'
        }
    ];

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Inventory & Assets</h2>
                    <p className="text-muted-foreground">Track school equipment and resources.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchAssets} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Item
                    </Button>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-4">
                <Card className="glass border-none">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Items</CardTitle>
                        <Package className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{assets.reduce((acc, curr) => acc + curr.quantity, 0)}</div>
                    </CardContent>
                </Card>
                <Card className="glass border-none">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Categories</CardTitle>
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{new Set(assets.map(a => a.category)).size}</div>
                    </CardContent>
                </Card>
                <Card className="glass border-none">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Under Maintenance</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{assets.filter(a => a.status !== 'Functional').length}</div>
                    </CardContent>
                </Card>
            </div>

            <Card className="glass border-none">
                <CardHeader>
                    <CardTitle>Inventory List</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={assets} 
                        loading={loading}
                        searchKey="name"
                    />
                </CardContent>
            </Card>
        </div>
    );
};

export default Assets;
