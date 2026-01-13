import { Invoice, ExtractResponse } from '@/types/invoice';

const API_BASE_URL = 'http://localhost:8080';

export class ApiClient {
  static async extractInvoice(file: File): Promise<ExtractResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/extract`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: 'Upload failed',
        message: response.statusText,
      }));
      throw new Error(error.message || 'Failed to extract invoice');
    }

    return response.json();
  }

  static async getInvoiceById(invoiceId: string): Promise<Invoice> {
    const response = await fetch(`${API_BASE_URL}/invoice/${invoiceId}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: 'Fetch failed',
        message: response.statusText,
      }));
      throw new Error(error.message || 'Failed to fetch invoice');
    }

    return response.json();
  }

  static async getInvoicesByVendor(vendorName: string): Promise<Invoice[]> {
    const response = await fetch(
      `${API_BASE_URL}/invoices/vendor/${encodeURIComponent(vendorName)}`
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: 'Fetch failed',
        message: response.statusText,
      }));
      throw new Error(error.message || 'Failed to fetch invoices');
    }

    return response.json();
  }
}
