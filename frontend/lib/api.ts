import { Invoice, ExtractResponse, BackendExtractResponse, BackendInvoiceResponse, BackendVendorResponse, BackendExtractItem, BackendInvoiceItem } from '@/types/invoice';

const API_BASE_URL = 'http://localhost:8080';

// Helper function to normalize POST /extract response
function normalizeExtractData(backendData: BackendExtractResponse['data']): Invoice {
  return {
    invoiceId: backendData.InvoiceId,
    vendorName: backendData.VendorName,
    invoiceNumber: backendData.InvoiceId,
    invoiceDate: backendData.InvoiceDate,
    dueDate: '', // Not provided by backend
    totalAmount: backendData.InvoiceTotal,
    currency: 'USD',
    status: 'Pending',
    subtotal: backendData.AmountDue || undefined,
    taxAmount: undefined,
    shippingCost: backendData.ShippingCost || undefined,
    shippingAddress: backendData.ShippingAddress,
    billingAddress: undefined,
    billingRecipient: backendData.CustomerName || undefined,
    items: backendData.Items?.map((item: BackendExtractItem) => ({
      description: item.Description || item.Name || '',
      quantity: item.Quantity || 0,
      unitPrice: item.UnitPrice || 0,
      amount: item.Amount,
    })),
  };
}

// Helper function to normalize GET /invoice/{id} response
function normalizeInvoiceResponse(response: any): Invoice {
  console.log('normalizeInvoiceResponse called with:', response);
  
  // Direct invoice object format: {InvoiceId, VendorName, Items, ...}
  if (!response) {
    console.error('Response is null or undefined');
    throw new Error('Invalid invoice data: response is null');
  }
  
  if (!response.InvoiceId) {
    console.error('Missing InvoiceId in response:', response);
    throw new Error('Invalid invoice data: missing InvoiceId');
  }
  
  const itemsData = response.Items || [];
  
  // Map and filter items
  const mappedItems = itemsData
    ?.filter((item: any) => {
      // Filter out invalid items: must have description or name, and valid amount
      const hasDescription = item.Description || item.Name;
      const hasValidAmount = item.Amount != null && !isNaN(item.Amount) && item.Amount !== 0;
      return hasDescription && hasValidAmount;
    })
    .map((item: any) => ({
      description: item.Description || item.Name || '',
      quantity: item.Quantity || 0,
      unitPrice: item.UnitPrice || 0,
      amount: item.Amount || 0,
    }));
  
  // Deduplicate items based on description, quantity, unitPrice, and amount
  const uniqueItems = mappedItems?.filter((item, index, self) =>
    index === self.findIndex((t) =>
      t.description === item.description &&
      t.quantity === item.quantity &&
      t.unitPrice === item.unitPrice &&
      t.amount === item.amount
    )
  );
  
  return {
    invoiceId: response.InvoiceId,
    vendorName: response.VendorName || 'Unknown',
    invoiceNumber: response.InvoiceId,
    invoiceDate: response.InvoiceDate || '',
    dueDate: '', // Not provided by backend
    totalAmount: response.InvoiceTotal || 0,
    currency: 'USD',
    status: 'Pending',
    subtotal: response.SubTotal || undefined,
    taxAmount: undefined,
    shippingCost: response.ShippingCost || undefined,
    shippingAddress: response.ShippingAddress || '',
    billingAddress: undefined,
    billingRecipient: response.BillingAddressRecipient || undefined,
    items: uniqueItems,
  };
}

export class ApiClient {
  static async extractInvoice(file: File): Promise<ExtractResponse> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Sending request to:', `${API_BASE_URL}/extract`);
      
      const response = await fetch(`${API_BASE_URL}/extract`, {
        method: 'POST',
        body: formData,
        mode: 'cors',
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          error: 'Upload failed',
          message: response.statusText,
        }));
        throw new Error(error.message || 'Failed to extract invoice');
      }

      // Get response text first to debug
      const responseText = await response.text();
      console.log('Backend raw response:', responseText.substring(0, 500));
      
      let backendResponse: BackendExtractResponse;
      try {
        backendResponse = JSON.parse(responseText);
        console.log('Parsed response:', backendResponse);
      } catch (parseError) {
        console.error('JSON parse error:', parseError);
        console.error('Raw response:', responseText);
        throw new Error('Backend returned invalid JSON. Check console for details.');
      }
      
      const normalizedInvoice = normalizeExtractData(backendResponse.data);
      console.log('Normalized invoice:', normalizedInvoice);
      
      return {
        invoiceId: normalizedInvoice.invoiceId,
        message: 'Invoice extracted successfully',
        invoice: normalizedInvoice,
      };
    } catch (error) {
      console.error('Full error:', error);
      
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        throw new Error('Cannot connect to backend server. Please ensure the backend is running at http://localhost:8080');
      }
      
      if (error instanceof Error) {
        throw error;
      }
      
      throw new Error('An unexpected error occurred');
    }
  }

  static async getInvoiceById(invoiceId: string): Promise<Invoice> {
    try {
      console.log('Fetching invoice:', invoiceId);
      const response = await fetch(`${API_BASE_URL}/invoice/${invoiceId}`);

      console.log('Invoice response status:', response.status);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Invoice not found');
        }
        const error = await response.json().catch(() => ({
          error: 'Fetch failed',
          message: response.statusText,
        }));
        throw new Error(error.message || 'Failed to fetch invoice');
      }

      const responseText = await response.text();
      console.log('Invoice raw response length:', responseText.length);
      console.log('Invoice raw response (first 1000 chars):', responseText.substring(0, 1000));
      
      if (!responseText || responseText.trim() === '') {
        console.error('Backend returned empty response');
        throw new Error('Backend returned empty response');
      }
      
      let backendResponse: any;
      try {
        backendResponse = JSON.parse(responseText);
        console.log('Parsed invoice response type:', typeof backendResponse);
        console.log('Parsed invoice response keys:', backendResponse ? Object.keys(backendResponse) : 'null/undefined');
        console.log('Full parsed response:', backendResponse);
        
        // Log each top-level property
        if (backendResponse) {
          for (const key in backendResponse) {
            console.log(`Response.${key}:`, backendResponse[key]);
          }
        }
      } catch (parseError) {
        console.error('JSON parse error:', parseError);
        console.error('Failed to parse:', responseText);
        throw new Error('Backend returned invalid JSON');
      }
      
      if (!backendResponse) {
        console.error('Parsed response is null or undefined');
        throw new Error('Backend returned null or undefined');
      }
      
      console.log('About to call normalizeInvoiceResponse with:', backendResponse);
      const normalized = normalizeInvoiceResponse(backendResponse);
      console.log('Normalized invoice:', normalized);
      return normalized;
    } catch (error) {
      console.error('Get invoice error:', error);
      throw error;
    }
  }

  static async getInvoicesByVendor(vendorName: string): Promise<Invoice[]> {
    try {
      console.log('Fetching invoices for vendor:', vendorName);
      console.log('Request URL:', `${API_BASE_URL}/invoices/vendor/${encodeURIComponent(vendorName)}`);
      
      const response = await fetch(
        `${API_BASE_URL}/invoices/vendor/${encodeURIComponent(vendorName)}`
      );

      console.log('Vendor search response status:', response.status);

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          error: 'Fetch failed',
          message: response.statusText,
        }));
        throw new Error(error.message || 'Failed to fetch invoices');
      }

      const responseText = await response.text();
      console.log('Vendor search raw response:', responseText.substring(0, 1000));
      
      let backendResponse: any;
      try {
        backendResponse = JSON.parse(responseText);
        console.log('Parsed vendor response:', backendResponse);
        console.log('Vendor response keys:', backendResponse ? Object.keys(backendResponse) : 'null');
      } catch (parseError) {
        console.error('JSON parse error:', parseError);
        throw new Error('Backend returned invalid JSON');
      }
      
      // Check if response has the expected structure
      if (backendResponse.VendorName && backendResponse.invoices) {
        // Expected format: { VendorName, TotalInvoices, invoices: [...] }
        console.log(`Found ${backendResponse.TotalInvoices || backendResponse.invoices.length} invoices for vendor: ${backendResponse.VendorName}`);
        
        if (!backendResponse.invoices || backendResponse.invoices.length === 0) {
          return [];
        }
        
        // Log the first invoice to see its structure
        console.log('First invoice structure:', backendResponse.invoices[0]);
        console.log('First invoice JSON:', JSON.stringify(backendResponse.invoices[0], null, 2));
        console.log('Has InvoiceId?', backendResponse.invoices[0].InvoiceId);
        console.log('Has invoice property?', backendResponse.invoices[0].invoice);
        console.log('Has items property?', backendResponse.invoices[0].items);
        console.log('All invoices array:', backendResponse.invoices);
        
        // Invoices are direct objects: {InvoiceId, VendorName, Items, ...}
        const normalized = backendResponse.invoices.map((invoice: any, index: number) => {
          console.log(`Processing invoice ${index}, ID:`, invoice.InvoiceId);
          console.log(`Invoice ${index} full object:`, invoice);
          const result = normalizeInvoiceResponse(invoice);
          console.log(`Normalized invoice ${index}:`, result);
          return result;
        });
        
        console.log('All normalized invoices:', normalized);
        return normalized;
      } else if (Array.isArray(backendResponse)) {
        // Handle array of invoices directly
        console.log(`Found ${backendResponse.length} invoices (array format)`);
        const normalized = backendResponse.map((item: any) => 
          normalizeInvoiceResponse(item)
        );
        console.log('Normalized invoices:', normalized);
        return normalized;
      } else if (backendResponse.InvoiceId) {
        // Single invoice object
        console.log('Single invoice returned');
        return [normalizeInvoiceResponse(backendResponse)];
      } else {
        console.error('Unexpected vendor response format:', backendResponse);
        throw new Error('Unexpected response format from backend');
      }
    } catch (error) {
      console.error('Vendor search error:', error);
      throw error;
    }
  }
}
