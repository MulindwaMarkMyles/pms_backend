# Payments API Documentation

Base URL: `/api/payments/`  
All endpoints require `Authorization: Bearer <token>` header.

## 1. Payment Statuses (`PaymentStatus`)

### List Statuses
GET `/payment-statuses/`

Response:
```json
[
  {"id":1, "name":"Pending"},
  {"id":2, "name":"Paid"},
  {"id":3, "name":"Overdue"},
  {"id":4, "name":"Partial"}
]
```

### Create Status
POST `/payment-statuses/`

Request:
```json
{ "name": "Processing" }
```

Response (201):
```json
{ "id":5, "name":"Processing" }
```

---

## 2. Payments (`Payment`)

### List All Payments
GET `/payments/`

Optional query params:
- `tenant_id` (e.g. `?tenant_id=1`)
- `status_id` (e.g. `?status_id=2`)
- `month` and `year` (e.g. `?month=1&year=2024`)

Response:
```json
[
  {
    "id":1,
    "tenant":1,
    "amount":"500000.00",
    "status":2,
    "due_date":"2024-01-31",
    "paid_at":"2024-01-30T14:30:00Z",
    "payment_for_month":1,
    "payment_for_year":2024,
    "payment_method":"Mobile Money",
    "reference_number":"TXN123456",
    "receipt_file":"/media/payment_receipts/1.jpg",
    "notes":"January rent"
  }
]
```

### Get Single Payment
GET `/payments/{id}/`

Response: same structure as above for one record

### Create Payment (Admin/Manager)
POST `/payments/`

Request:
```json
{
  "tenant":1,
  "amount":500000,
  "status":1,
  "due_date":"2024-01-31",
  "payment_for_month":1,
  "payment_for_year":2024,
  "notes":"January rent"
}
```

Response (201):
```json
{
  "id":5,
  "tenant":1,
  "amount":"500000.00",
  "status":1,
  "due_date":"2024-01-31",
  "payment_for_month":1,
  "payment_for_year":2024,
  "paid_at":null,
  "payment_method":null,
  "reference_number":null,
  "receipt_file":null,
  "notes":"January rent"
}
```

### Tenant: Log Payment with Receipt
POST `/payments/log_payment/`

Request (form-data):
- `amount`, `due_date`, `payment_for_month`, `payment_for_year`
- `payment_method`, `reference_number`, `notes`
- `receipt_file` (file)

Response (201):
```json
{
  "message":"Payment logged successfully. Property manager will verify and update status.",
  "payment":{ ...payment object... }
}
```

### Update Payment Status
PATCH `/payments/{id}/update_payment_status/`

Request:
```json
{
  "status_id":2,
  "months_paid":[1,2],
  "payment_method":"Bank Transfer",
  "reference_number":"TXN987654"
}
```

Response:
```json
{
  "message":"Payment status updated successfully",
  "months_paid":[1,2]
}
```

---

## 3. Quick Filters & Reports

### Pending Payments
GET `/payments/pending_payments/`

### Overdue Payments
GET `/payments/overdue_payments/`

### Tenant's Own Payments
GET `/payments/my_payments/`

### Tenant's Rent Alerts
GET `/payments/my_rent_alerts/`

### Manager Alerts
GET `/payments/payment_alerts/`

---

## Error Responses

- **400 Bad Request**: missing fields or invalid data
  ```json
  {"error":"due_date is required"}
  ```

- **404 Not Found**: invalid `tenant` or payment ID
  ```json
  {"error":"Payment not found"}
  ```

- **401 Unauthorized**: missing or invalid token
  ```json
  {"detail":"Authentication credentials were not provided."}
  ```

---

**Notes:**
- `receipt_file` returns a URL to download the uploaded file.
- Use filters to narrow down by tenant, status, month, or year.
- All endpoints require a valid JWT access token.