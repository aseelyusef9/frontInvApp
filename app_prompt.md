# Build a Next.js Invoice Parser Frontend

## Project Overview
Build a modern, production-quality Next.js application that serves strictly as a FRONTEND for an existing Invoice Parser BACKEND API.
The backend is already implemented and running.  
The frontend must connect to this backend and consume its endpoints without modifying or reimplementing any backend logic.

The application allows users to upload invoice documents, trigger invoice extraction, and view extracted invoice details returned by the backend.

## Backend API
Base URL: http://localhost:8080

The backend already exists.
Do NOT create, modify, or simulate backend functionality.
Use real HTTP requests to the endpoints below.

### Available Endpoints
- POST `/extract`
  - Upload an invoice file using multipart/form-data
  - Triggers invoice extraction and returns extracted invoice data
- GET `/invoice/{invoice_id}`
  - Retrieve details of a specific invoice by InvoiceId
- GET `/invoices/vendor/{vendor_name}`
  - Retrieve invoices filtered by vendor name

## Technical Requirements

### Framework & Setup
- Use **Next.js** with App Router
- Use **TypeScript** for full type safety
- Use **Tailwind CSS** for styling
- Use a UI component library for consistent design (e.g. shadcn/ui or equivalent)

## Application Pages & Routing (Multi-Page Application)

Implement the following pages exactly according to this specification:

### 1. Login Page (`/login`)
- Simple login form with username and password fields
- Dummy authentication only:
  - Username: `admin`
  - Password: `admin`
- Authentication is frontend-only for UI demonstration purposes
- Store authentication state in localStorage or sessionStorage
- Redirect to `/dashboard` after successful login
- No backend authentication integration is required

### 2. Dashboard (`/dashboard`)
- High-level overview page
- Display statistics cards (e.g. total invoices, recent uploads)
- Quick actions section (Upload Invoice, Search by Vendor)
- Navigation menu to all application pages

### 3. Upload Invoice Page (`/upload`)
- Drag-and-drop file upload area with click-to-select support
- Validate supported file types (PDF and image formats)
- Upload files using the backend endpoint:
  - POST `/extract`
- Display loading spinner/progress indicator during upload
- Show success and error notifications based on API response

### 4. Invoices List Page (`/invoices`)
- Display invoices in a table or grid layout
- Invoice data must be retrieved from the backend API
- Support filtering UI (status, date range) and sorting on the frontend
- Implement pagination or lazy loading on the frontend
- Selecting an invoice navigates to the invoice details page

### 5. Invoice Details Page (`/invoice/[id]`)
- Fetch invoice data from:
  - GET `/invoice/{invoice_id}`
- Display extracted invoice information in a structured layout
- Editable fields with client-side validation only
- Download invoice option (UI only if backend does not support file download)
- Back navigation to the invoices list

## Data & State Handling
- The frontend must remain stateless with regard to invoice data
- Do NOT persist invoices or API responses in localStorage or sessionStorage
- Always fetch invoice data directly from the backend API
- The backend API is the single source of truth

## Styling Guidelines
- Implement a modern, clean, professional UI
- Enterprise-grade design (Oracle-inspired color palette preferred)
- Consistent spacing, typography, and component usage
- Improve visual hierarchy and user experience
- Avoid default or boilerplate styling

## Final Notes
- This is a FRONTEND-ONLY implementation
- Do NOT generate backend code or mock data
- Do NOT invent new API endpoints
- The frontend must strictly follow the API contract provided above


UI & State Decisions:
Use shadcn/ui (built on Radix UI) as the primary component library to ensure accessible, professional, and enterprise-grade UI components aligned with modern Next.js standards. Manage application state using React Context and client-side hooks for authentication and temporary UI state only, keeping invoice data stateless and always fetched from the backend API. Authentication state should be persisted using sessionStorage so users remain logged in across page refreshes, with logout occurring only via an explicit Logout action. Use a toast notification library (prefer sonner) to provide clear success and error feedback for backend interactions such as invoice uploads, improving overall user experience.

Decisions:
- Authentication should persist across browser restarts, so store an auth flag in localStorage and log out only via an explicit Logout action (which clears localStorage).
- Invoice listing is supported only via the existing backend endpoints: GET /invoices/vendor/{vendor_name} for list/search and GET /invoice/{invoice_id} for details. There is no “fetch all invoices” requirement; the /invoices page is vendor-driven (search by vendor), and the details page is ID-driven.
- Editable fields on the invoice details page are UI-only for demonstration purposes. Do not submit updates to the backend and do not invent PUT/PATCH endpoints.

Invoice retrieval is handled through two distinct mechanisms with a clear separation of concerns:
- Vendor name is provided as a path parameter to the backend API endpoint (GET /invoices/vendor/{vendor_name}), but it is not a frontend route parameter. In the frontend, vendor is treated as a UI-level filter on the /invoices page and triggers data fetching without changing the application route.
- Invoice ID is a frontend route parameter used for navigation to the invoice details page (/invoice/[id]) and is passed to the backend API endpoint (GET /invoice/{invoice_id}) to retrieve a specific invoice.
