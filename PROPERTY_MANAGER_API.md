# Property Manager API Documentation

## 1. Core Property Management Modules

### Create Estate
**POST** `/api/core/estates/`
```json
{
    "name": "Sunset Gardens Estate",
    "address": "123 Main Street, Kampala, Uganda",
    "size": "5 acres",
    "description": "Luxury residential estate with modern amenities"
}
```

### Create Block
**POST** `/api/core/blocks/`
```json
{
    "estate": 1,
    "name": "Block A",
    "description": "First residential block with 20 units"
}
```

### Create Apartment
**POST** `/api/core/apartments/`
```json
{
    "block": 1,
    "number": "A101",
    "size": 120.50,
    "amenities": [1, 2, 3],
    "furnishings": [1, 2],
    "rent_amount": 500000,
    "number_of_rooms": 3,
    "color": "White",
    "description": "3-bedroom apartment with modern furnishings"
}
```

### Create Amenities (Pre-populate)
**POST** `/api/core/amenities/`
```json
{
    "name": "Water"
}
```
```json
{
    "name": "Electricity"
}
```
```json
{
    "name": "Internet"
}
```
```json
{
    "name": "Parking"
}
```
```json
{
    "name": "Security"
}
```

### Create Furnishings (Pre-populate)
**POST** `/api/core/furnishings/`
```json
{
    "name": "Air Conditioning"
}
```
```json
{
    "name": "Kitchen Appliances"
}
```
```json
{
    "name": "Bedroom Furniture"
}
```
```json
{
    "name": "Living Room Furniture"
}
```

### Get Available Apartments
**GET** `/api/core/apartments/available/`
Response:
```json
[
    {
        "id": 1,
        "block": {
            "id": 1,
            "name": "Block A",
            "estate": {
                "id": 1,
                "name": "Sunset Gardens Estate"
            }
        },
        "number": "A101",
        "size": "120.50",
        "amenities": [
            {"id": 1, "name": "Water"},
            {"id": 2, "name": "Electricity"}
        ],
        "furnishings": [
            {"id": 1, "name": "Air Conditioning"}
        ]
    }
]
```

## 2. Tenant Management Module

### Create Tenant Types (Pre-populate)
**POST** `/api/tenants/tenant-types/`
```json
{
    "name": "Short Stay (6 months or less)"
}
```
```json
{
    "name": "Long Term Stay (1+ years)"
}
```
```json
{
    "name": "Corporate Tenant"
}
```

### Create Tenant and Map to Apartment
**POST** `/api/tenants/tenants/`
```json
{
    "user": {
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "securepassword123"
    },
    "tenant_type": 1,
    "apartment": 1,
    "lease_start": "2024-01-01",
    "lease_end": "2024-12-31",
    "phone_number": "+256700123456",
    "emergency_contact": "Jane Doe - +256700123457"
}
```

### Get Tenants by Estate
**GET** `/api/tenants/tenants/by_estate/?estate_id=1`

### Filter Tenants by Apartment
**GET** `/api/tenants/tenants/?apartment_id=1`

### Filter Tenants by Type
**GET** `/api/tenants/tenants/?tenant_type_id=1`

## 3. Complaint Handling Module

### Create Complaint Status (Pre-populate)
**POST** `/api/complaints/complaint-statuses/`
```json
{
    "name": "Open"
}
```
```json
{
    "name": "In Progress"
}
```
```json
{
    "name": "Resolved"
}
```
```json
{
    "name": "Closed"
}
```

### Get All Complaints
**GET** `/api/complaints/complaints/`

### Filter Complaints by Status
**GET** `/api/complaints/complaints/?status_id=1`

### Filter Complaints by Tenant
**GET** `/api/complaints/complaints/?tenant_id=1`

### Update Complaint Status and Provide Feedback
**PATCH** `/api/complaints/complaints/{complaint_id}/update_status/`
```json
{
    "status_id": 2,
    "feedback": "We have received your complaint and our maintenance team will address it within 24 hours."
}
```

### Close Complaint
**PATCH** `/api/complaints/complaints/{complaint_id}/close/`
```json
{}
```

## 4. Rent Payment Management

### Create Payment Status (Pre-populate)
**POST** `/api/payments/payment-statuses/`
```json
{
    "name": "Pending"
}
```
```json
{
    "name": "Paid"
}
```
```json
{
    "name": "Overdue"
}
```
```json
{
    "name": "Partial"
}
```

### Create Payment Record
**POST** `/api/payments/payments/`
```json
{
    "tenant": 1,
    "amount": 500000,
    "status": 1,
    "due_date": "2024-01-31",
    "payment_for_month": 1,
    "payment_for_year": 2024
}
```

### Update Payment Status
**PATCH** `/api/payments/payments/{payment_id}/update_payment_status/`
```json
{
    "status_id": 2,
    "months_paid": [1, 2],
    "paid_amount": 500000,
    "payment_method": "Bank Transfer",
    "reference_number": "TXN123456789"
}
```

### Get Pending Payments
**GET** `/api/payments/payments/pending_payments/`

### Get Overdue Payments
**GET** `/api/payments/payments/overdue_payments/`

### Filter Payments by Month/Year
**GET** `/api/payments/payments/?month=1&year=2024`

### Filter Payments by Tenant
**GET** `/api/payments/payments/?tenant_id=1`

### Filter Payments by Status
**GET** `/api/payments/payments/?status_id=1`

## Authentication

### Get JWT Token
**POST** `/api/token/`
```json
{
    "username": "property_manager",
    "password": "your_password"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Use Token in Headers
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

## API Endpoints Summary

### Core Property Management
- `POST /api/core/estates/` - Create estate
- `GET /api/core/estates/` - List estates
- `POST /api/core/blocks/` - Create block
- `GET /api/core/blocks/?estate_id=1` - Get blocks by estate
- `POST /api/core/apartments/` - Create apartment
- `GET /api/core/apartments/available/` - Get available apartments
- `POST /api/core/amenities/` - Create amenity
- `POST /api/core/furnishings/` - Create furnishing

### Tenant Management
- `POST /api/tenants/tenant-types/` - Create tenant type
- `POST /api/tenants/tenants/` - Create tenant
- `GET /api/tenants/tenants/by_estate/?estate_id=1` - Get tenants by estate

### Complaint Handling
- `GET /api/complaints/complaints/` - List complaints
- `PATCH /api/complaints/complaints/{id}/update_status/` - Update complaint
- `PATCH /api/complaints/complaints/{id}/close/` - Close complaint

### Payment Management
- `POST /api/payments/payments/` - Create payment
- `PATCH /api/payments/payments/{id}/update_payment_status/` - Update payment
- `GET /api/payments/payments/pending_payments/` - Get pending payments
- `GET /api/payments/payments/overdue_payments/` - Get overdue payments