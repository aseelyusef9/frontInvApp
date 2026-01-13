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
