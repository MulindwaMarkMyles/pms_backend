# Property Management System (PMS) Backend API Documentation

## Overview
This is the backend API for a Property Management System built with Django REST Framework. The system manages estates, apartments, tenants, and payments.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All API endpoints require authentication. Include the authorization header:
```
Authorization: Bearer <your-token>
```

---

## 🏠 Core APIs

### Estates
- `GET /estates/` - List all estates
- `POST /estates/` - Create a new estate
- `GET /estates/{id}/` - Get estate details
- `PUT /estates/{id}/` - Update estate
- `DELETE /estates/{id}/` - Delete estate

### Blocks
- `GET /blocks/` - List all blocks
- `POST /blocks/` - Create a new block
- `GET /blocks/{id}/` - Get block details
- `PUT /blocks/{id}/` - Update block
- `DELETE /blocks/{id}/` - Delete block

### Apartments
- `GET /apartments/` - List all apartments
- `POST /apartments/` - Create a new apartment
- `GET /apartments/{id}/` - Get apartment details
- `PUT /apartments/{id}/` - Update apartment
- `DELETE /apartments/{id}/` - Delete apartment

---

## 👥 Tenant APIs

### Base Endpoints
- `GET /tenants/` - List all tenants
- `POST /tenants/` - Create a new tenant
- `GET /tenants/{id}/` - Get tenant details
- `PUT /tenants/{id}/` - Update tenant
- `PATCH /tenants/{id}/` - Partial update tenant
- `DELETE /tenants/{id}/` - Delete tenant

### Query Parameters
- `apartment_id` - Filter tenants by apartment
- `tenant_type_id` - Filter tenants by tenant type

### Custom Endpoints

#### Get Tenants by Estate
```
GET /tenants/by_estate/?estate_id={estate_id}
```
Returns all tenants in a specific estate.

#### Tenancy Expiry Dashboard
```
GET /tenants/expiry_dashboard/
```
Returns comprehensive dashboard data including:
- Tenants expiring in next 30 days
- Expired leases
- Monthly expiry counts
- Renewal rate statistics

**Response:**
```json
{
  "expiring_soon": [
    {
      "tenant_id": 1,
      "tenant_name": "John Doe",
      "apartment": "A101",
      "lease_end": "2024-02-15",
      "days_until_expiry": 15,
      "estate": "Sunrise Estate",
      "block": "Block A"
    }
  ],
  "expired_leases": [...],
  "expiring_this_month": 5,
  "expiring_next_month": 3,
  "expired_total": 2,
  "renewal_rate": 85.5
}
```

#### Get Expiring Tenants
```
GET /tenants/expiring/?start_date=2024-01-01&end_date=2024-01-31
```
Returns tenants expiring within a specific date range.

### Creating a Tenant

**Endpoint:** `POST /tenants/`

**Request Body:**
```json
{
  "user": {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe"
  },
  "apartment": 1,
  "tenant_type": 1,
  "lease_start": "2024-01-01",
  "lease_end": "2024-12-31",
  "phone_number": "+1234567890",
  "emergency_contact": "Jane Doe - +0987654321"
}
```

**Response:**
```json
{
  "message": "Tenant created successfully",
  "tenant": {
    "id": 1,
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "tenant_type": 1,
    "apartment": 1,
    "lease_start": "2024-01-01",
    "lease_end": "2024-12-31",
    "phone_number": "+1234567890",
    "emergency_contact": "Jane Doe - +0987654321"
  }
}
```

### Updating a Tenant

**Endpoint:** `PUT /tenants/{id}/` or `PATCH /tenants/{id}/`

**Request Body:**
```json
{
  "user": {
    "first_name": "John Updated",
    "email": "john.updated@example.com"
  },
  "apartment": 2,
  "lease_end": "2025-01-01",
  "phone_number": "+1111111111"
}
```

---

## 💳 Payment APIs

### Base Endpoints
- `GET /payments/` - List all payments
- `POST /payments/` - Create a new payment
- `GET /payments/{id}/` - Get payment details
- `PUT /payments/{id}/` - Update payment
- `DELETE /payments/{id}/` - Delete payment

### Query Parameters
- `tenant_id` - Filter payments by tenant
- `status` - Filter by payment status (pending, completed, failed)
- `payment_type` - Filter by payment type (rent, deposit, utilities)
- `date_from` - Filter payments from date
- `date_to` - Filter payments to date

### Custom Payment Endpoints

#### Tenant Payment History
```
GET /payments/tenant/{tenant_id}/history/
```
Get complete payment history for a specific tenant.

#### Monthly Payment Summary
```
GET /payments/monthly_summary/?month=2024-01&estate_id=1
```
Get payment summary for a specific month and estate.

#### Outstanding Payments
```
GET /payments/outstanding/
```
Get all outstanding/pending payments.

#### Payment Dashboard
```
GET /payments/dashboard/
```
Get payment analytics including:
- Total collected this month
- Outstanding amounts
- Payment trends
- Top paying tenants

**Response:**
```json
{
  "total_collected_this_month": 50000.00,
  "outstanding_amount": 15000.00,
  "payment_success_rate": 92.5,
  "pending_payments_count": 8,
  "monthly_trend": [
    {"month": "2024-01", "amount": 45000},
    {"month": "2024-02", "amount": 50000}
  ]
}
```

### Creating a Payment

**Endpoint:** `POST /payments/`

**Request Body:**
```json
{
  "tenant": 1,
  "amount": 1500.00,
  "payment_type": "rent",
  "payment_method": "bank_transfer",
  "reference_number": "TXN123456789",
  "payment_date": "2024-01-15",
  "due_date": "2024-01-01",
  "description": "January 2024 Rent Payment",
  "status": "completed"
}
```

### Payment Status Updates

**Endpoint:** `PATCH /payments/{id}/status/`

**Request Body:**
```json
{
  "status": "completed",
  "notes": "Payment verified and processed"
}
```

---

## 📊 Tenant Types

### Endpoints
- `GET /tenant-types/` - List all tenant types
- `POST /tenant-types/` - Create tenant type
- `GET /tenant-types/{id}/` - Get tenant type details
- `PUT /tenant-types/{id}/` - Update tenant type
- `DELETE /tenant-types/{id}/` - Delete tenant type

---

## 🔐 Authentication APIs

### Login
```
POST /auth/login/
```
**Request:**
```json
{
  "username": "admin",
  "password": "password"
}
```

### Logout
```
POST /auth/logout/
```

### Token Refresh
```
POST /auth/token/refresh/
```

---

## 📋 Common Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {...},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Error message",
  "details": "Detailed error information"
}
```

### Validation Error
```json
{
  "field_name": ["This field is required"],
  "another_field": ["Invalid value"]
}
```

---

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access API Documentation**
   - Swagger UI: `http://localhost:8000/swagger/`
   - ReDoc: `http://localhost:8000/redoc/`

---

## 📝 Notes

- All dates should be in ISO format (YYYY-MM-DD)
- Monetary amounts are in decimal format with 2 decimal places
- All timestamps are in UTC
- File uploads are supported for payment receipts and tenant documents

---

## 🛠️ Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid data |
| 401 | Unauthorized - Invalid credentials |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error |

---

## 📞 Support

For API support and questions, contact the development team or refer to the project documentation.