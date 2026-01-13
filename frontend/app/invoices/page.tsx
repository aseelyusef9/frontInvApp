'use client';

import { useState, useMemo } from 'react';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ApiClient } from '@/lib/api';
import { Invoice } from '@/types/invoice';
import { toast } from 'sonner';

type SortField = 'invoiceDate' | 'dueDate' | 'totalAmount' | 'vendorName';
type SortOrder = 'asc' | 'desc';

export default function InvoicesPage() {
  const [vendorName, setVendorName] = useState('');
  const [invoiceId, setInvoiceId] = useState('');
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchType, setSearchType] = useState<'vendor' | 'id'>('vendor');
  
  // Filtering state
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  
  // Sorting state
  const [sortField, setSortField] = useState<SortField>('invoiceDate');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  
  const router = useRouter();

  const handleSearchByVendor = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!vendorName.trim()) {
      toast.error('Please enter a vendor name');
      return;
    }

    setIsLoading(true);
    setHasSearched(true);
    setSearchType('vendor');
    setCurrentPage(1); // Reset to first page on new search

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

  const handleSearchById = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!invoiceId.trim()) {
      toast.error('Please enter an invoice ID');
      return;
    }

    setIsLoading(true);
    setHasSearched(true);
    setSearchType('id');
    setCurrentPage(1); // Reset to first page on new search

    try {
      const result = await ApiClient.getInvoiceById(invoiceId);
      setInvoices([result]);
      toast.success('Invoice found');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Invoice not found');
      setInvoices([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Filter, sort, and paginate invoices
  const processedInvoices = useMemo(() => {
    let filtered = [...invoices];

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(
        (invoice) => invoice.status?.toLowerCase() === statusFilter.toLowerCase()
      );
    }

    // Apply date range filter
    if (startDate) {
      filtered = filtered.filter(
        (invoice) => new Date(invoice.invoiceDate) >= new Date(startDate)
      );
    }
    if (endDate) {
      filtered = filtered.filter(
        (invoice) => new Date(invoice.invoiceDate) <= new Date(endDate)
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];

      // Handle date and amount comparisons
      if (sortField === 'invoiceDate' || sortField === 'dueDate') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      } else if (sortField === 'totalAmount') {
        aValue = Number(aValue);
        bValue = Number(bValue);
      } else {
        aValue = String(aValue).toLowerCase();
        bValue = String(bValue).toLowerCase();
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [invoices, statusFilter, startDate, endDate, sortField, sortOrder]);

  // Calculate pagination
  const totalPages = Math.ceil(processedInvoices.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedInvoices = processedInvoices.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  const handleFilterChange = () => {
    setCurrentPage(1);
  };

  const handleSortChange = (field: SortField) => {
    if (sortField === field) {
      // Toggle sort order if clicking the same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
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

            {/* Search Cards */}
            <div className="grid gap-6 md:grid-cols-2">
              {/* Search by Vendor */}
              <Card>
                <CardHeader>
                  <CardTitle>Search by Vendor</CardTitle>
                  <CardDescription>
                    Enter a vendor name to retrieve associated invoices
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSearchByVendor} className="space-y-4">
                    <div>
                      <Label htmlFor="vendorName">Vendor Name</Label>
                      <Input
                        id="vendorName"
                        type="text"
                        placeholder="Enter vendor name..."
                        value={vendorName}
                        onChange={(e) => setVendorName(e.target.value)}
                        disabled={isLoading}
                      />
                    </div>
                    <Button type="submit" disabled={isLoading} className="w-full">
                      {isLoading && searchType === 'vendor' ? 'Searching...' : 'Search by Vendor'}
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Search by Invoice ID */}
              <Card>
                <CardHeader>
                  <CardTitle>Search by Invoice ID</CardTitle>
                  <CardDescription>
                    Enter an invoice ID to view specific invoice
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSearchById} className="space-y-4">
                    <div>
                      <Label htmlFor="invoiceId">Invoice ID</Label>
                      <Input
                        id="invoiceId"
                        type="text"
                        placeholder="Enter invoice ID..."
                        value={invoiceId}
                        onChange={(e) => setInvoiceId(e.target.value)}
                        disabled={isLoading}
                      />
                    </div>
                    <Button type="submit" disabled={isLoading} className="w-full">
                      {isLoading && searchType === 'id' ? 'Searching...' : 'Search by ID'}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Results */}
            {hasSearched && (
              <Card>
                <CardHeader>
                  <CardTitle>Search Results</CardTitle>
                  <CardDescription>
                    {processedInvoices.length > 0
                      ? `Showing ${paginatedInvoices.length} of ${processedInvoices.length} invoice(s)${searchType === 'vendor' ? ` for "${vendorName}"` : ''}`
                      : searchType === 'vendor' 
                        ? `No invoices found for "${vendorName}"`
                        : `No invoice found with ID "${invoiceId}"`}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Filters and Controls */}
                  {invoices.length > 0 && (
                    <div className="space-y-4">
                      <div className="grid gap-4 md:grid-cols-4">
                        {/* Status Filter */}
                        <div>
                          <Label htmlFor="statusFilter">Status</Label>
                          <Select
                            value={statusFilter}
                            onValueChange={(value) => {
                              setStatusFilter(value);
                              handleFilterChange();
                            }}
                          >
                            <SelectTrigger id="statusFilter">
                              <SelectValue placeholder="All Statuses" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="all">All Statuses</SelectItem>
                              <SelectItem value="paid">Paid</SelectItem>
                              <SelectItem value="pending">Pending</SelectItem>
                              <SelectItem value="overdue">Overdue</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        {/* Start Date Filter */}
                        <div>
                          <Label htmlFor="startDate">Start Date</Label>
                          <Input
                            id="startDate"
                            type="date"
                            value={startDate}
                            onChange={(e) => {
                              setStartDate(e.target.value);
                              handleFilterChange();
                            }}
                          />
                        </div>

                        {/* End Date Filter */}
                        <div>
                          <Label htmlFor="endDate">End Date</Label>
                          <Input
                            id="endDate"
                            type="date"
                            value={endDate}
                            onChange={(e) => {
                              setEndDate(e.target.value);
                              handleFilterChange();
                            }}
                          />
                        </div>

                        {/* Items Per Page */}
                        <div>
                          <Label htmlFor="itemsPerPage">Items Per Page</Label>
                          <Select
                            value={itemsPerPage.toString()}
                            onValueChange={(value) => {
                              setItemsPerPage(Number(value));
                              setCurrentPage(1);
                            }}
                          >
                            <SelectTrigger id="itemsPerPage">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="5">5</SelectItem>
                              <SelectItem value="10">10</SelectItem>
                              <SelectItem value="20">20</SelectItem>
                              <SelectItem value="50">50</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      {/* Clear Filters */}
                      {(statusFilter !== 'all' || startDate || endDate) && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setStatusFilter('all');
                            setStartDate('');
                            setEndDate('');
                            setCurrentPage(1);
                          }}
                        >
                          Clear Filters
                        </Button>
                      )}
                    </div>
                  )}

                  {/* Table */}
                  {paginatedInvoices.length > 0 ? (
                    <div className="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Invoice #</TableHead>
                            <TableHead
                              className="cursor-pointer hover:bg-stone-100"
                              onClick={() => handleSortChange('vendorName')}
                            >
                              <div className="flex items-center gap-1">
                                Vendor
                                {sortField === 'vendorName' && (
                                  <span className="text-xs">
                                    {sortOrder === 'asc' ? '↑' : '↓'}
                                  </span>
                                )}
                              </div>
                            </TableHead>
                            <TableHead
                              className="cursor-pointer hover:bg-stone-100"
                              onClick={() => handleSortChange('invoiceDate')}
                            >
                              <div className="flex items-center gap-1">
                                Date
                                {sortField === 'invoiceDate' && (
                                  <span className="text-xs">
                                    {sortOrder === 'asc' ? '↑' : '↓'}
                                  </span>
                                )}
                              </div>
                            </TableHead>
                            <TableHead
                              className="cursor-pointer hover:bg-stone-100"
                              onClick={() => handleSortChange('dueDate')}
                            >
                              <div className="flex items-center gap-1">
                                Due Date
                                {sortField === 'dueDate' && (
                                  <span className="text-xs">
                                    {sortOrder === 'asc' ? '↑' : '↓'}
                                  </span>
                                )}
                              </div>
                            </TableHead>
                            <TableHead
                              className="cursor-pointer hover:bg-stone-100"
                              onClick={() => handleSortChange('totalAmount')}
                            >
                              <div className="flex items-center gap-1">
                                Amount
                                {sortField === 'totalAmount' && (
                                  <span className="text-xs">
                                    {sortOrder === 'asc' ? '↑' : '↓'}
                                  </span>
                                )}
                              </div>
                            </TableHead>
                            <TableHead>Status</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {paginatedInvoices.map((invoice) => (
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
                        {statusFilter !== 'all' || startDate || endDate
                          ? 'Try adjusting your filters'
                          : 'Try searching with a different vendor name'}
                      </p>
                    </div>
                  )}

                  {/* Pagination */}
                  {processedInvoices.length > 0 && totalPages > 1 && (
                    <div className="flex items-center justify-between border-t pt-4">
                      <div className="text-sm text-stone-600">
                        Showing {startIndex + 1} to {Math.min(endIndex, processedInvoices.length)} of{' '}
                        {processedInvoices.length} results
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                          disabled={currentPage === 1}
                        >
                          Previous
                        </Button>
                        <div className="flex items-center gap-1">
                          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                            let pageNumber;
                            if (totalPages <= 5) {
                              pageNumber = i + 1;
                            } else if (currentPage <= 3) {
                              pageNumber = i + 1;
                            } else if (currentPage >= totalPages - 2) {
                              pageNumber = totalPages - 4 + i;
                            } else {
                              pageNumber = currentPage - 2 + i;
                            }
                            
                            return (
                              <Button
                                key={pageNumber}
                                variant={currentPage === pageNumber ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => setCurrentPage(pageNumber)}
                                className="w-10"
                              >
                                {pageNumber}
                              </Button>
                            );
                          })}
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                          disabled={currentPage === totalPages}
                        >
                          Next
                        </Button>
                      </div>
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
