// Backend response structures (from backend prompt)

// POST /extract response
export interface BackendExtractResponse {
  confidence: number;
  data: {
    VendorName: string;
    VendorNameLogo: string;
    InvoiceId: string;
    InvoiceDate: string;
    ShippingAddress: string;
    CustomerName: string | null;
    AmountDue: number | null;
    ShippingCost: number | null;
    InvoiceTotal: number;
    Items: BackendExtractItem[];
  };
  dataConfidence: {
    VendorName: number;
    InvoiceId: number;
    InvoiceDate: number;
    ShippingAddress: number;
    CustomerName: number;
    AmountDue: number;
    ShippingCost: number;
    InvoiceTotal: number;
    Items: number;
  };
  predictionTime: number;
}

export interface BackendExtractItem {
  Description: string | null;
  Name: string | null;
  Quantity: number | null;
  UnitPrice: number | null;
  Amount: number;
  InvoiceId: string;
}

// GET /invoice/{invoice_id} response
export interface BackendInvoiceResponse {
  invoice: {
    InvoiceId: string;
    VendorName: string;
    InvoiceDate: string;
    ShippingAddress: string;
    BillingAddressRecipient: string | null;
    SubTotal: number | null;
    ShippingCost: number | null;
    InvoiceTotal: number;
  };
  items: BackendInvoiceItem[];
}

export interface BackendInvoiceItem {
  id: number;
  InvoiceId: string;
  Name: string | null;
  Description: string | null;
  Quantity: number | null;
  UnitPrice: number | null;
  Amount: number;
}

// GET /invoices/vendor/{vendor_name} response
export interface BackendVendorResponse {
  VendorName: string;
  TotalInvoices: number;
  invoices: Array<{
    invoice: {
      InvoiceId: string;
      VendorName: string;
      InvoiceDate: string;
      ShippingAddress: string;
      BillingAddressRecipient: string | null;
      SubTotal: number | null;
      ShippingCost: number | null;
      InvoiceTotal: number;
    };
    items: BackendInvoiceItem[];
  }>;
}

// Frontend normalized structure
export interface Invoice {
  invoiceId: string;
  vendorName: string;
  invoiceNumber: string;
  invoiceDate: string;
  dueDate: string;
  totalAmount: number;
  currency: string;
  status: string;
  items?: InvoiceItem[];
  billingAddress?: string;
  shippingAddress?: string;
  taxAmount?: number;
  subtotal?: number;
  shippingCost?: number;
  billingRecipient?: string;
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: number;
  amount: number;
}

export interface ExtractResponse {
  invoiceId: string;
  message: string;
  invoice: Invoice;
}

export interface ApiError {
  error: string;
  message: string;
  statusCode?: number;
}
