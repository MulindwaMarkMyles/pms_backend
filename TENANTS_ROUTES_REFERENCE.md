# Tenants API - Complete Routes Reference

Base URL: `/api/tenants/`  
All endpoints require `Authorization: Bearer <token>` header.

## 1. Tenant Types Routes

### GET - List All Tenant Types
**Route:** `GET /tenant-types/`

**Request:** No body required

**Response:**
```json
[
  {
    "id": 1,
    "name": "Short Stay (≤6 months)",
    "description": "Tenants with lease duration of 6 months or less",
    "created_at": "2024-01-15T10:00:00Z"
  },
  {
    "id": 2,
    "name": "Long Term (≥1 year)",
    "description": "Tenants with lease duration of 1 year or more",
    "created_at": "2024-01-15T10:05:00Z"
  },
  {
    "id": 3,
    "name": "Corporate",
    "description": "Company-sponsored tenants",
    "created_at": "2024-01-15T10:10:00Z"
  }
]
```

### GET - Single Tenant Type
**Route:** `GET /tenant-types/{id}/`

**Request:** No body required

**Response:**
```json
{
  "id": 1,
  "name": "Short Stay (≤6 months)",
  "description": "Tenants with lease duration of 6 months or less",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### POST - Create Tenant Type
**Route:** `POST /tenant-types/`

**Required Fields:**
- `name` (string, max 100 chars, unique)

**Optional Fields:**
- `description` (text)

**Request:**
```json
{
  "name": "Student Housing",
  "description": "Housing for university students"
}
```

**Response (201):**
```json
{
  "id": 4,
  "name": "Student Housing", 
  "description": "Housing for university students",
  "created_at": "2024-01-26T14:30:00Z"
}
```

---

## 2. Tenants Routes

### GET - List All Tenants
**Route:** `GET /tenants/`

**Query Parameters:**
- `apartment_id` (integer) - Filter by apartment
- `tenant_type_id` (integer) - Filter by tenant type
- `estate_id` (integer) - Filter by estate (via apartment)

**Examples:**
- `GET /tenants/` - All tenants
- `GET /tenants/?apartment_id=5` - Tenants in apartment 5
- `GET /tenants/?tenant_type_id=2` - Long-term tenants only

**Request:** No body required

**Response:**
```json
[
  {
    "id": 1,
    "user_details": {
      "id": 5,
      "username": "jane_doe",
      "email": "jane@example.com", 
      "first_name": "Jane",
      "last_name": "Doe"
    },
    "tenant_type": 2,
    "tenant_type_details": {
      "id": 2,
      "name": "Long Term (≥1 year)"
    },
    "apartment": 4,
    "apartment_details": {
      "id": 4,
      "number": "A101",
      "block": {
        "id": 1,
        "name": "Block A",
        "estate": {
          "id": 1,
          "name": "Sunset Gardens"
        }
      }
    },
    "lease_start": "2024-01-01",
    "lease_end": "2024-12-31",
    "phone_number": "+256700123456",
    "emergency_contact": "+256700123457",
    "created_at": "2024-01-10T12:00:00Z"
  }
]
```

### GET - Single Tenant
**Route:** `GET /tenants/{id}/`

**Request:** No body required

**Response:** Single tenant object (same structure as list above)

### GET - Tenants by Estate
**Route:** `GET /tenants/by_estate/`

**Query Parameters:**
- `estate_id` (required integer) - Estate ID to filter by

**Example:** `GET /tenants/by_estate/?estate_id=1`

**Request:** No body required

**Response:** Array of tenant objects (same structure as list above)

### GET - Tenancy Expiry Dashboard
**Route:** `GET /tenants/expiry_dashboard/`

**Request:** No body required

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
      "estate": "Sunset Gardens",
      "block": "Block A"
    }
  ],
  "expired_leases": [
    {
      "tenant_id": 2,
      "tenant_name": "Jane Smith",
      "apartment": "B202",
      "lease_end": "2024-01-10", 
      "days_overdue": 20,
      "estate": "City Heights",
      "block": "Block B"
    }
  ],
  "expiring_this_month": 8,
  "expiring_next_month": 12,
  "expired_total": 3,
  "renewal_rate": 75.0
}
```

### GET - Tenants Expiring in Date Range
**Route:** `GET /tenants/expiring/`

**Query Parameters:**
- `start_date` (required, YYYY-MM-DD format)
- `end_date` (required, YYYY-MM-DD format)

**Example:** `GET /tenants/expiring/?start_date=2024-01-01&end_date=2024-01-31`

**Request:** No body required

**Response:**
```json
{
  "period": "2024-01-01 to 2024-01-31",
  "expiring_tenants": [
    {
      "tenant_id": 1,
      "tenant_name": "John Doe",
      "apartment": "A101",
      "lease_end": "2024-01-31",
      "estate": "Sunset Gardens", 
      "block": "Block A"
    }
  ],
  "count": 8
}
```

### POST - Create Tenant
**Route:** `POST /tenants/`

**Required Fields:**
- `user` (object) - User account details
  - `username` (string, unique)
  - `email` (string, unique, valid email)
  - `password` (string, min 8 chars)
  - `first_name` (string)
  - `last_name` (string)
- `tenant_type` (integer) - Must exist
- `apartment` (integer) - Must exist and be available
- `lease_start` (date, YYYY-MM-DD format)
- `lease_end` (date, YYYY-MM-DD format)

**Optional Fields:**
- `phone_number` (string, max 20 chars)
- `emergency_contact` (string, max 200 chars)

**Request:**
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
  "apartment": 3,
  "lease_start": "2024-02-01",
  "lease_end": "2024-08-01",
  "phone_number": "+256700123458",
  "emergency_contact": "Emergency: Jane Doe - +256700123459"
}
```

**Response (201):**
```json
{
  "message": "Tenant created successfully",
  "tenant": {
    "id": 2,
    "user": {
      "id": 7,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John", 
      "last_name": "Doe"
    },
    "tenant_type": 1,
    "apartment": 3,
    "lease_start": "2024-02-01",
    "lease_end": "2024-08-01",
    "phone_number": "+256700123458",
    "emergency_contact": "Emergency: Jane Doe - +256700123459",
    "created_at": "2024-01-26T15:30:00Z"
  }
}
```

### PUT - Update Tenant (Complete)
**Route:** `PUT /tenants/{id}/`

**Request:** All fields required (same as POST, but without user.password)

**Response (200):** Updated tenant object

### PATCH - Update Tenant (Partial)
**Route:** `PATCH /tenants/{id}/`

**Request:** Only fields to update
```json
{
  "lease_end": "2024-09-01",
  "phone_number": "+256700999888"
}
```

**Response (200):** Updated tenant object

### DELETE - Delete Tenant
**Route:** `DELETE /tenants/{id}/`

**Request:** No body required

**Response (204):** No content

---

## Validation Rules & Constraints

### Tenant Type Validation
- `name`: Required, unique, max 100 characters
- `description`: Optional, unlimited text

### Tenant Validation
- **User validation:**
  - `username`: Required, unique, max 150 characters
  - `email`: Required, unique, valid email format
  - `password`: Required, min 8 characters (only for creation)
  - `first_name`/`last_name`: Required, max 150 characters each
- **Tenant validation:**
  - `tenant_type`: Required, must reference existing TenantType
  - `apartment`: Required, must reference existing available Apartment
  - `lease_start`: Required, valid date
  - `lease_end`: Required, valid date, must be after lease_start
  - `phone_number`: Optional, max 20 characters
  - `emergency_contact`: Optional, max 200 characters

### Business Rules
- **Apartment Occupancy**: One tenant per apartment (enforced by unique constraint)
- **Lease Dates**: End date must be after start date
- **User Account**: Each tenant gets a Django User account for login

---

## Common Error Responses

### 400 Bad Request - Missing Required Fields
```json
{
  "error": "Validation failed",
  "details": {
    "user": {
      "username": ["This field is required."],
      "email": ["This field is required."]
    },
    "apartment": ["This field is required."]
  }
}
```

### 400 Bad Request - Invalid Foreign Key
```json
{
  "error": "Validation failed", 
  "details": {
    "apartment": ["Invalid pk \"999\" - object does not exist."],
    "tenant_type": ["Invalid pk \"99\" - object does not exist."]
  }
}
```

### 400 Bad Request - Apartment Already Occupied
```json
{
  "error": "Apartment is already occupied by another tenant"
}
```

### 400 Bad Request - Username/Email Already Exists
```json
{
  "error": "Validation failed",
  "details": {
    "user": {
      "username": ["A user with that username already exists."],
      "email": ["User with this Email already exists."]
    }
  }
}
```

### 400 Bad Request - Invalid Date Range
```json
{
  "error": "Validation failed",
  "details": {
    "lease_end": ["Lease end date must be after lease start date."]
  }
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## Example Usage Flow

### 1. List Available Apartments
```bash
curl -X GET "http://127.0.0.1:8000/api/core/apartments/available/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. List Tenant Types  
```bash
curl -X GET "http://127.0.0.1:8000/api/tenants/tenant-types/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Create New Tenant
```bash
curl -X POST "http://127.0.0.1:8000/api/tenants/tenants/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "username": "alice_smith",
      "email": "alice@example.com", 
      "first_name": "Alice",
      "last_name": "Smith",
      "password": "mysecurepass123"
    },
    "tenant_type": 2,
    "apartment": 5,
    "lease_start": "2024-03-01",
    "lease_end": "2025-02-28",
    "phone_number": "+256700555444",
    "emergency_contact": "Bob Smith - +256700555445"
  }'
```

### 4. List Tenants by Estate
```bash
curl -X GET "http://127.0.0.1:8000/api/tenants/tenants/by_estate/?estate_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Update Tenant Info
```bash
curl -X PATCH "http://127.0.0.1:8000/api/tenants/tenants/2/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+256700111222",
    "lease_end": "2025-03-31"
  }'
```

---

**Notes:**
- All tenant endpoints automatically create User accounts for login
- Apartment becomes "occupied" when assigned to tenant
- Use filters to narrow down tenant lists by apartment, type, or estate
- Lease dates are validated to ensure logical date ranges
- Phone numbers support international formats