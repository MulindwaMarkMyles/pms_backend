# Tenant API Documentation

Base URL: `/api/`  
All endpoints require `Authorization: Bearer <token>` header.  
**Note**: Tenant must be logged in; APIs automatically filter by authenticated tenant.

## 1. Receive Rent Due Alerts

### Get My Rent Alerts
GET `/payments/payments/my_rent_alerts/`

Response:
```json
{
  "upcoming_due":[
    {
      "id":1,
      "amount":"500000.00",
      "due_date":"2024-02-15",
      "payment_for_month":2,
      "payment_for_year":2024,
      "status_details":{"name":"Pending"},
      "days_until_due":5
    }
  ],
  "overdue":[
    {
      "id":2,
      "amount":"500000.00",
      "due_date":"2024-01-15",
      "payment_for_month":1,
      "payment_for_year":2024,
      "status_details":{"name":"Overdue"},
      "days_overdue":20
    }
  ],
  "total_upcoming":1,
  "total_overdue":1
}
```

---

## 2. View Payment Receipt Status

### Get Payment Acknowledgement Status
GET `/payments/payments/payment_receipt_status/`

Response:
```json
{
  "payments":[
    {
      "id":1,
      "amount":"500000.00",
      "due_date":"2024-01-31",
      "paid_at":"2024-01-30T14:30:00Z",
      "payment_for_month":1,
      "payment_for_year":2024,
      "status":"Paid",
      "payment_method":"Mobile Money",
      "reference_number":"TXN123456789",
      "receipt_file":"/media/payment_receipts/receipt_123.jpg",
      "acknowledgement_status":"Acknowledged"
    },
    {
      "id":2,
      "amount":"500000.00",
      "due_date":"2024-02-29",
      "paid_at":null,
      "payment_for_month":2,
      "payment_for_year":2024,
      "status":"Processing",
      "payment_method":"Bank Transfer",
      "reference_number":"TXN987654321",
      "receipt_file":"/media/payment_receipts/receipt_124.jpg",
      "acknowledgement_status":"Pending"
    }
  ],
  "total_paid":1,
  "total_pending":1
}
```

### Get All My Payments
GET `/payments/payments/my_payments/`

Response: Array of payment objects (same structure as above)

---

## 3. Log Complaint

### Get Available Categories
GET `/complaints/complaints/complaint_categories/`

Response:
```json
[
  {
    "id":1,
    "name":"Amenities",
    "description":"Issues with water, electricity, internet, etc."
  },
  {
    "id":2,
    "name":"Maintenance",
    "description":"Repairs needed for apartment fixtures"
  },
  {
    "id":3,
    "name":"Security",
    "description":"Security-related concerns"
  },
  {
    "id":4,
    "name":"Noise",
    "description":"Noise complaints from neighbors"
  },
  {
    "id":5,
    "name":"Cleanliness",
    "description":"Common area cleanliness issues"
  }
]
```

### Log New Complaint
POST `/complaints/complaints/log_complaint/`

Request (JSON or form-data):
```json
{
  "category":1,
  "title":"Water leak in kitchen",
  "description":"There is a persistent water leak under the kitchen sink that has been ongoing for 3 days. The leak is causing water damage to the cabinet.",
  "attachment":"file_object_or_base64_string"
}
```

Response (201):
```json
{
  "message":"Complaint logged successfully. Property manager will respond soon.",
  "complaint":{
    "id":15,
    "category":{
      "id":1,
      "name":"Amenities"
    },
    "title":"Water leak in kitchen",
    "description":"There is a persistent water leak under the kitchen sink...",
    "status":{
      "id":1,
      "name":"Open"
    },
    "created_at":"2024-01-26T10:30:00Z",
    "attachment":"/media/complaint_attachments/leak_photo.jpg"
  }
}
```

### Get My Complaints
GET `/complaints/complaints/my_complaints/`

Response:
```json
[
  {
    "id":15,
    "category":{
      "id":1,
      "name":"Amenities"
    },
    "title":"Water leak in kitchen",
    "description":"There is a persistent water leak...",
    "status":{
      "id":2,
      "name":"In Progress"
    },
    "feedback":"Maintenance team scheduled for tomorrow morning.",
    "created_at":"2024-01-26T10:30:00Z",
    "updated_at":"2024-01-26T15:45:00Z",
    "attachment":"/media/complaint_attachments/leak_photo.jpg"
  }
]
```

---

## 4. Log Payment and Attach Receipt

### Log Payment with Receipt
POST `/payments/payments/log_payment/`

Request (form-data):
```
amount: 500000
payment_method: Mobile Money
reference_number: TXN123456789
payment_for_month: 1
payment_for_year: 2024
due_date: 2024-01-31
receipt_file: [file object]
notes: Payment made via MTN Mobile Money
```

Request (JSON alternative):
```json
{
  "amount":500000,
  "payment_method":"Mobile Money",
  "reference_number":"TXN123456789",
  "payment_for_month":1,
  "payment_for_year":2024,
  "due_date":"2024-01-31",
  "notes":"Payment made via MTN Mobile Money"
}
```

Response (201):
```json
{
  "message":"Payment logged successfully. Property manager will verify and update status.",
  "payment":{
    "id":25,
    "amount":"500000.00",
    "payment_method":"Mobile Money",
    "reference_number":"TXN123456789",
    "payment_for_month":1,
    "payment_for_year":2024,
    "due_date":"2024-01-31",
    "status":{
      "id":3,
      "name":"Processing"
    },
    "receipt_file":"/media/payment_receipts/receipt_25.jpg",
    "notes":"Payment made via MTN Mobile Money",
    "created_at":"2024-01-26T16:30:00Z"
  }
}
```

---

## File Upload Guidelines

### Supported Formats
- **Payment Receipts**: JPG, PNG, PDF, GIF
- **Complaint Attachments**: JPG, PNG, PDF, GIF

### File Size Limits
- Maximum file size: 10MB per file
- Accepted MIME types: `image/*`, `application/pdf`

### Upload Paths
- Payment receipts: `/media/payment_receipts/`
- Complaint attachments: `/media/complaint_attachments/`

---

## Error Responses

### 400 Bad Request
```json
{
  "error":"category is required"
}
```

### 404 Not Found
```json
{
  "error":"Tenant profile not found"
}
```

### 401 Unauthorized
```json
{
  "detail":"Authentication credentials were not provided."
}
```

### 413 Payload Too Large
```json
{
  "error":"File size exceeds maximum limit of 10MB"
}
```

---

## SMS Alert Configuration

### Rent Due Alerts
- **Trigger**: Preconfigured days before due date (default: 7 days)
- **Content**: Amount due, due date, payment methods
- **Frequency**: Daily reminders until payment confirmed

### Payment Confirmations
- **Trigger**: When payment status changes to "Paid"
- **Content**: Payment confirmation, amount, receipt number

### Complaint Updates
- **Trigger**: When complaint status changes
- **Content**: Status update, feedback from property manager

---

**Notes:**
- All tenant endpoints automatically filter by authenticated user
- File uploads support both multipart/form-data and base64 encoding
- SMS alerts are sent automatically based on system configuration
- Payment logging sets status to "Processing" until manager verification