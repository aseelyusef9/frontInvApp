'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import Navigation from '@/components/Navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { ApiClient } from '@/lib/api';
import { Invoice } from '@/types/invoice';
import { toast } from 'sonner';

export default function InvoicesPage() {
  const [vendorName, setVendorName] = useState('');
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const router = useRouter();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!vendorName.trim()) {
      toast.error('Please enter a vendor name');
      return;
    }

    setIsLoading(true);
    setHasSearched(true);

    try {
      const results = await ApiClient.getInvoicesByVendor(vendorName);
      setInvoices(results);
      
      if (results.length === 0) {
        toast.info('No invoices found for this vendor');
      } else {
        toast.success(`Found ${results.length} invoice(s)`);
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to fetch invoices');
      setInvoices([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRowClick = (invoiceId: string) => {
    router.push(`/invoice/${invoiceId}`);
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-stone-100 text-stone-800';
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-stone-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <div className="space-y-6">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold text-stone-900">Invoices</h1>
              <p className="text-stone-600 mt-2">
                Search and manage invoices by vendor
              </p>
            </div>

            {/* Search Card */}
            <Card>
              <CardHeader>
                <CardTitle>Search by Vendor</CardTitle>
                <CardDescription>
                  Enter a vendor name to retrieve associated invoices
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSearch} className="flex gap-4">
                  <div className="flex-1">
                    <Label htmlFor="vendorName" className="sr-only">
                      Vendor Name
                    </Label>
                    <Input
                      id="vendorName"
                      type="text"
                      placeholder="Enter vendor name..."
                      value={vendorName}
                      onChange={(e) => setVendorName(e.target.value)}
                      disabled={isLoading}
                    />
                  </div>
                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? 'Searching...' : 'Search'}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Results */}
            {hasSearched && (
              <Card>
                <CardHeader>
                  <CardTitle>Search Results</CardTitle>
                  <CardDescription>
                    {invoices.length > 0
                      ? `Showing ${invoices.length} invoice(s) for "${vendorName}"`
                      : `No invoices found for "${vendorName}"`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {invoices.length > 0 ? (
                    <div className="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Invoice #</TableHead>
                            <TableHead>Vendor</TableHead>
                            <TableHead>Date</TableHead>
                            <TableHead>Due Date</TableHead>
                            <TableHead>Amount</TableHead>
                            <TableHead>Status</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {invoices.map((invoice) => (
                            <TableRow
                              key={invoice.invoiceId}
                              onClick={() => handleRowClick(invoice.invoiceId)}
                              className="cursor-pointer hover:bg-stone-50"
                            >
                              <TableCell className="font-medium">
                                {invoice.invoiceNumber || invoice.invoiceId.substring(0, 8)}
                              </TableCell>
                              <TableCell>{invoice.vendorName}</TableCell>
                              <TableCell>{formatDate(invoice.invoiceDate)}</TableCell>
                              <TableCell>{formatDate(invoice.dueDate)}</TableCell>
                              <TableCell className="font-medium">
                                {formatCurrency(invoice.totalAmount, invoice.currency)}
                              </TableCell>
                              <TableCell>
                                <Badge
                                  variant="secondary"
                                  className={getStatusColor(invoice.status)}
                                >
                                  {invoice.status || 'Unknown'}
                                </Badge>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <svg
                        className="mx-auto h-12 w-12 text-stone-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                      <h3 className="mt-2 text-sm font-semibold text-stone-900">
                        No invoices found
                      </h3>
                      <p className="mt-1 text-sm text-stone-500">
                        Try searching with a different vendor name
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Help Card */}
            {!hasSearched && (
              <Card>
                <CardHeader>
                  <CardTitle>How to Search</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex gap-3">
                    <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-stone-900 text-white text-xs font-bold">
                      1
                    </div>
                    <p className="text-sm text-stone-700">
                      Enter the exact vendor name in the search field above
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-stone-900 text-white text-xs font-bold">
                      2
                    </div>
                    <p className="text-sm text-stone-700">
                      Click "Search" to retrieve all invoices from that vendor
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-stone-900 text-white text-xs font-bold">
                      3
                    </div>
                    <p className="text-sm text-stone-700">
                      Click on any invoice row to view detailed information
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
