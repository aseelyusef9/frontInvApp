'use client';

import ProtectedRoute from '@/components/ProtectedRoute';
import Navigation from '@/components/Navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-stone-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <div className="space-y-8">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold text-stone-900">Dashboard</h1>
              <p className="text-stone-600 mt-2">
                Welcome to Invoice Parser - Your document management hub
              </p>
            </div>

            {/* Statistics Cards */}
            <div className="grid gap-6 md:grid-cols-3">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Total Invoices</CardDescription>
                  <CardTitle className="text-4xl">-</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-stone-600">
                    Search by vendor to view invoices
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Recent Uploads</CardDescription>
                  <CardTitle className="text-4xl">-</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-stone-600">
                    Upload invoices to get started
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Processing Status</CardDescription>
                  <CardTitle className="text-4xl">Ready</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-stone-600">
                    System is ready to process invoices
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Get started with common tasks
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <Link href="/upload">
                  <Button className="w-full h-24 text-lg" size="lg">
                    <div className="flex flex-col items-center gap-2">
                      <svg
                        className="w-8 h-8"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                      </svg>
                      <span>Upload Invoice</span>
                    </div>
                  </Button>
                </Link>

                <Link href="/invoices">
                  <Button
                    variant="outline"
                    className="w-full h-24 text-lg"
                    size="lg"
                  >
                    <div className="flex flex-col items-center gap-2">
                      <svg
                        className="w-8 h-8"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        />
                      </svg>
                      <span>Search Invoices</span>
                    </div>
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Getting Started */}
            <Card>
              <CardHeader>
                <CardTitle>Getting Started</CardTitle>
                <CardDescription>
                  Learn how to use the Invoice Parser system
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-stone-900 text-white text-sm font-bold">
                    1
                  </div>
                  <div>
                    <h3 className="font-semibold">Upload an Invoice</h3>
                    <p className="text-sm text-stone-600">
                      Upload PDF or image files containing invoice data. The system will automatically extract key information.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-stone-900 text-white text-sm font-bold">
                    2
                  </div>
                  <div>
                    <h3 className="font-semibold">Search by Vendor</h3>
                    <p className="text-sm text-stone-600">
                      Use the Invoices page to search for invoices by vendor name and view detailed information.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-stone-900 text-white text-sm font-bold">
                    3
                  </div>
                  <div>
                    <h3 className="font-semibold">Review and Edit</h3>
                    <p className="text-sm text-stone-600">
                      Click on any invoice to view details and make necessary edits to the extracted data.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
