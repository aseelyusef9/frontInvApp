# Invoice Parser Frontend

A modern, production-quality Next.js frontend application for the Invoice Parser system.

## Features

- **Authentication**: Dummy login system (admin/admin)
- **Dashboard**: Overview with statistics and quick actions
- **Upload Invoice**: Drag-and-drop file upload with validation
- **Invoices List**: Search invoices by vendor name
- **Invoice Details**: View and edit invoice information

## Tech Stack

- **Next.js 16** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **shadcn/ui** component library
- **Sonner** for toast notifications

## Prerequisites

- Node.js 18+ installed
- Backend API running at `http://localhost:8080`

## Installation

```bash
cd frontend
npm install
```

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will start at `http://localhost:3000`

### Production Build

```bash
npm run build
npm start
```

## Login Credentials

- **Username**: `admin`
- **Password**: `admin`

## Application Routes

- `/` - Root (redirects to login or dashboard)
- `/login` - Login page
- `/dashboard` - Main dashboard with overview
- `/upload` - Upload invoice files
- `/invoices` - Search and list invoices by vendor
- `/invoice/[id]` - View and edit invoice details

## Backend API Integration

The frontend connects to the backend API at `http://localhost:8080` with the following endpoints:

- `POST /extract` - Upload and extract invoice
- `GET /invoice/{invoice_id}` - Get invoice by ID
- `GET /invoices/vendor/{vendor_name}` - Get invoices by vendor

## Features Details

### Authentication
- Persisted in localStorage
- Protected routes redirect to login
- Logout clears authentication state

### Upload Invoice
- Drag-and-drop or click to select
- Validates file type (PDF, JPG, PNG, GIF)
- 10MB file size limit
- Redirects to invoice details after successful upload

### Invoices List
- Search by vendor name
- Table view with sorting capabilities
- Click row to view details
- Status badges with color coding

### Invoice Details
- View all invoice information
- Edit mode for UI demonstration (not submitted to backend)
- Display line items if available
- Back navigation to invoices list

## Styling

The application uses a professional, Oracle-inspired color palette based on the Stone color scheme from Tailwind CSS, providing an enterprise-grade look and feel.

## Notes

- Authentication is frontend-only for demonstration purposes
- Invoice data is always fetched from the backend (stateless frontend)
- Edit functionality is UI-only and does not persist to the backend
- All API calls include proper error handling with toast notifications

