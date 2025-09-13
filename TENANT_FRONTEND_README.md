# Tenant APIs - User Profile 3

This document provides a comprehensive guide for frontend developers to integrate with the Tenant APIs for the Property Management System.

## 🔐 Authentication

All tenant APIs require authentication. Include the JWT token in the Authorization header:

```javascript
headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
}
```

## Base URL
```
http://127.0.0.1:8000
```

---

## 📱 1. Receive Rent Due Alerts

### **Get Rent Due Alerts**
**GET** `/api/payments/payments/my_rent_alerts/`

**Description:** Get rent due alerts for the logged-in tenant based on preconfigured days from due date.

**Request:**
```javascript
fetch('/api/payments/payments/my_rent_alerts/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
```

**Response:**
```json
{
    "upcoming_due": [
        {
            "id": 1,
            "amount": "500000.00",
            "due_date": "2024-01-31",
            "payment_for_month": 1,
            "payment_for_year": 2024,
            "status_details": {
                "name": "Pending"
            },
            "days_until_due": 5
        }
    ],
    "overdue": [
        {
            "id": 2,
            "amount": "500000.00",
            "due_date": "2023-12-31",
            "payment_for_month": 12,
            "payment_for_year": 2023,
            "status_details": {
                "name": "Overdue"
            },
            "days_overdue": 15
        }
    ],
    "total_upcoming": 1,
    "total_overdue": 1
}
```

**Frontend Implementation:**
```javascript
const RentAlerts = () => {
    const [alerts, setAlerts] = useState(null);

    useEffect(() => {
        fetchRentAlerts();
    }, []);

    const fetchRentAlerts = async () => {
        try {
            const response = await fetch('/api/payments/payments/my_rent_alerts/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const data = await response.json();
            setAlerts(data);
        } catch (error) {
            console.error('Error fetching rent alerts:', error);
        }
    };

    return (
        <div className="rent-alerts">
            <h3>Rent Alerts</h3>
            
            {alerts?.overdue.length > 0 && (
                <div className="overdue-section">
                    <h4 className="text-red-600">Overdue Payments ({alerts.total_overdue})</h4>
                    {alerts.overdue.map(payment => (
                        <div key={payment.id} className="alert bg-red-100 p-4 mb-2 rounded">
                            <p><strong>Amount:</strong> UGX {payment.amount}</p>
                            <p><strong>Due:</strong> {payment.due_date}</p>
                            <p className="text-red-600"><strong>Overdue by:</strong> {payment.days_overdue} days</p>
                        </div>
                    ))}
                </div>
            )}
            
            {alerts?.upcoming_due.length > 0 && (
                <div className="upcoming-section">
                    <h4 className="text-yellow-600">Upcoming Due ({alerts.total_upcoming})</h4>
                    {alerts.upcoming_due.map(payment => (
                        <div key={payment.id} className="alert bg-yellow-100 p-4 mb-2 rounded">
                            <p><strong>Amount:</strong> UGX {payment.amount}</p>
                            <p><strong>Due:</strong> {payment.due_date}</p>
                            <p className="text-yellow-600"><strong>Due in:</strong> {payment.days_until_due} days</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
```

---

## 🧾 2. View Payment Receipt Status

### **Get Payment Receipt Status**
**GET** `/api/payments/payments/payment_receipt_status/`

**Description:** View payment acknowledgement status for the logged-in tenant.

**Request:**
```javascript
fetch('/api/payments/payments/payment_receipt_status/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
```

**Response:**
```json
{
    "payments": [
        {
            "id": 1,
            "amount": "500000.00",
            "due_date": "2024-01-31",
            "paid_at": "2024-01-30T14:30:00Z",
            "payment_for_month": 1,
            "payment_for_year": 2024,
            "status": "Paid",
            "payment_method": "Mobile Money",
            "reference_number": "TXN123456789",
            "receipt_file": "/media/payment_receipts/receipt_123.jpg",
            "acknowledgement_status": "Acknowledged"
        },
        {
            "id": 2,
            "amount": "500000.00",
            "due_date": "2024-02-29",
            "paid_at": null,
            "payment_for_month": 2,
            "payment_for_year": 2024,
            "status": "Processing",
            "payment_method": "Bank Transfer",
            "reference_number": "TXN987654321",
            "receipt_file": "/media/payment_receipts/receipt_124.jpg",
            "acknowledgement_status": "Pending"
        }
    ],
    "total_paid": 1,
    "total_pending": 1
}
```

**Frontend Implementation:**
```javascript
const PaymentReceipts = () => {
    const [payments, setPayments] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchPaymentStatus();
    }, []);

    const fetchPaymentStatus = async () => {
        try {
            const response = await fetch('/api/payments/payments/payment_receipt_status/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const data = await response.json();
            setPayments(data.payments);
        } catch (error) {
            console.error('Error fetching payment status:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status) => {
        const statusClasses = {
            'Paid': 'bg-green-100 text-green-800',
            'Processing': 'bg-yellow-100 text-yellow-800',
            'Pending': 'bg-blue-100 text-blue-800',
            'Overdue': 'bg-red-100 text-red-800'
        };
        return `px-2 py-1 rounded-full text-sm ${statusClasses[status] || 'bg-gray-100 text-gray-800'}`;
    };

    if (loading) return <div>Loading payment status...</div>;

    return (
        <div className="payment-receipts max-w-4xl mx-auto p-6">
            <h3 className="text-2xl font-bold mb-6">Payment Receipt Status</h3>
            
            <div className="payments-list space-y-4">
                {payments.map(payment => (
                    <div key={payment.id} className="payment-card bg-white border rounded-lg p-6 shadow-sm">
                        <div className="payment-header flex justify-between items-start mb-4">
                            <h4 className="text-xl font-semibold">UGX {payment.amount}</h4>
                            <span className={getStatusBadge(payment.status)}>
                                {payment.acknowledgement_status}
                            </span>
                        </div>
                        
                        <div className="payment-details grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <p><strong>Month:</strong> {payment.payment_for_month}/{payment.payment_for_year}</p>
                                <p><strong>Due Date:</strong> {payment.due_date}</p>
                                <p><strong>Payment Method:</strong> {payment.payment_method || 'N/A'}</p>
                                <p><strong>Reference:</strong> {payment.reference_number || 'N/A'}</p>
                            </div>
                            
                            <div>
                                {payment.paid_at && (
                                    <p><strong>Paid At:</strong> {new Date(payment.paid_at).toLocaleDateString()}</p>
                                )}
                                
                                {payment.receipt_file && (
                                    <div className="receipt-section mt-4">
                                        <a 
                                            href={payment.receipt_file} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                                        >
                                            View Receipt
                                        </a>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
            
            {payments.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                    No payment records found.
                </div>
            )}
        </div>
    );
};
```

### **Get All My Payments**
**GET** `/api/payments/payments/my_payments/`

**Description:** Get all payment records for the logged-in tenant.

**Response:** Same structure as payment_receipt_status but includes all payments, not just recent ones.

---

## 📝 3. Log Complaint

### **Get Complaint Categories**
**GET** `/api/complaints/complaints/complaint_categories/`

**Description:** Get pre-set complaint categories for apartment-related issues.

**Response:**
```json
[
    {
        "id": 1,
        "name": "Amenities",
        "description": "Issues with water, electricity, internet, etc."
    },
    {
        "id": 2,
        "name": "Maintenance",
        "description": "Repairs needed for apartment fixtures"
    },
    {
        "id": 3,
        "name": "Security",
        "description": "Security-related concerns"
    },
    {
        "id": 4,
        "name": "Noise",
        "description": "Noise complaints from neighbors"
    },
    {
        "id": 5,
        "name": "Cleanliness",
        "description": "Common area cleanliness issues"
    }
]
```

### **Log New Complaint**
**POST** `/api/complaints/complaints/log_complaint/`

**Description:** Submit a new complaint or support case.

**Request JSON:**
```json
{
    "category": 1,
    "title": "Water leak in kitchen",
    "description": "There is a persistent water leak under the kitchen sink that has been ongoing for 3 days. The leak is causing water damage to the cabinet.",
    "attachment": "file_object_or_base64_string"
}
```

**Response:**
```json
{
    "message": "Complaint logged successfully. Property manager will respond soon.",
    "complaint": {
        "id": 15,
        "category": {
            "id": 1,
            "name": "Amenities"
        },
        "title": "Water leak in kitchen",
        "description": "There is a persistent water leak under the kitchen sink...",
        "status": {
            "id": 1,
            "name": "Open"
        },
        "created_at": "2024-01-26T10:30:00Z",
        "attachment": "/media/complaint_attachments/leak_photo.jpg"
    }
}
```

### **Get My Complaints**
**GET** `/api/complaints/complaints/my_complaints/`

**Description:** Get all complaints logged by the current tenant.

**Response:**
```json
[
    {
        "id": 15,
        "category": {
            "id": 1,
            "name": "Amenities"
        },
        "title": "Water leak in kitchen",
        "description": "There is a persistent water leak...",
        "status": {
            "id": 2,
            "name": "In Progress"
        },
        "feedback": "Maintenance team scheduled for tomorrow morning.",
        "created_at": "2024-01-26T10:30:00Z",
        "updated_at": "2024-01-26T15:45:00Z",
        "attachment": "/media/complaint_attachments/leak_photo.jpg"
    }
]
```

**Frontend Implementation:**
```javascript
const ComplaintManager = () => {
    const [complaints, setComplaints] = useState([]);
    const [categories, setCategories] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        category: '',
        title: '',
        description: '',
        attachment: null
    });

    useEffect(() => {
        fetchComplaints();
        fetchCategories();
    }, []);

    const fetchComplaints = async () => {
        try {
            const response = await fetch('/api/complaints/complaints/my_complaints/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const data = await response.json();
            setComplaints(data);
        } catch (error) {
            console.error('Error fetching complaints:', error);
        }
    };

    const fetchCategories = async () => {
        try {
            const response = await fetch('/api/complaints/complaints/complaint_categories/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const data = await response.json();
            setCategories(data);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        const submitData = new FormData();
        submitData.append('category', formData.category);
        submitData.append('title', formData.title);
        submitData.append('description', formData.description);
        if (formData.attachment) {
            submitData.append('attachment', formData.attachment);
        }

        try {
            const response = await fetch('/api/complaints/complaints/log_complaint/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: submitData
            });

            if (response.ok) {
                const result = await response.json();
                alert(result.message);
                setShowForm(false);
                setFormData({ category: '', title: '', description: '', attachment: null });
                fetchComplaints(); // Refresh the list
            } else {
                const error = await response.json();
                alert('Error: ' + (error.error || 'Failed to submit complaint'));
            }
        } catch (error) {
            console.error('Error submitting complaint:', error);
            alert('Failed to submit complaint');
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            'Open': 'bg-blue-100 text-blue-800',
            'In Progress': 'bg-yellow-100 text-yellow-800',
            'Resolved': 'bg-green-100 text-green-800',
            'Closed': 'bg-gray-100 text-gray-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    };

    return (
        <div className="complaint-manager max-w-6xl mx-auto p-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold">My Complaints</h3>
                <button 
                    onClick={() => setShowForm(true)}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                    Log New Complaint
                </button>
            </div>

            {/* Complaint Form Modal */}
            {showForm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
                        <h4 className="text-xl font-bold mb-4">Log New Complaint</h4>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Category</label>
                                <select 
                                    value={formData.category}
                                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                                    required
                                    className="w-full border rounded px-3 py-2"
                                >
                                    <option value="">Select Category</option>
                                    {categories.map(cat => (
                                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                                    ))}
                                </select>
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium mb-1">Title</label>
                                <input 
                                    type="text"
                                    value={formData.title}
                                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                                    required
                                    className="w-full border rounded px-3 py-2"
                                    placeholder="Brief description of the issue"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium mb-1">Description</label>
                                <textarea 
                                    value={formData.description}
                                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                                    required
                                    rows="4"
                                    className="w-full border rounded px-3 py-2"
                                    placeholder="Detailed description of the problem"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium mb-1">Attachment (Optional)</label>
                                <input 
                                    type="file"
                                    onChange={(e) => setFormData({...formData, attachment: e.target.files[0]})}
                                    className="w-full border rounded px-3 py-2"
                                    accept="image/*,application/pdf"
                                />
                            </div>
                            
                            <div className="flex space-x-3">
                                <button 
                                    type="submit"
                                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                                >
                                    Submit Complaint
                                </button>
                                <button 
                                    type="button"
                                    onClick={() => setShowForm(false)}
                                    className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Complaints List */}
            <div className="complaints-list space-y-4">
                {complaints.map(complaint => (
                    <div key={complaint.id} className="complaint-card bg-white border rounded-lg p-6 shadow-sm">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h4 className="text-lg font-semibold">{complaint.title}</h4>
                                <p className="text-sm text-gray-600">
                                    Category: {complaint.category?.name || 'N/A'}
                                </p>
                            </div>
                            <span className={`px-2 py-1 rounded-full text-sm ${getStatusColor(complaint.status?.name)}`}>
                                {complaint.status?.name || 'Unknown'}
                            </span>
                        </div>
                        
                        <p className="text-gray-700 mb-4">{complaint.description}</p>
                        
                        {complaint.feedback && (
                            <div className="feedback-section bg-blue-50 p-3 rounded mb-4">
                                <h5 className="font-medium text-blue-800 mb-1">Property Manager Response:</h5>
                                <p className="text-blue-700">{complaint.feedback}</p>
                            </div>
                        )}
                        
                        <div className="complaint-meta flex justify-between items-center text-sm text-gray-500">
                            <span>Created: {new Date(complaint.created_at).toLocaleDateString()}</span>
                            {complaint.updated_at !== complaint.created_at && (
                                <span>Updated: {new Date(complaint.updated_at).toLocaleDateString()}</span>
                            )}
                        </div>
                        
                        {complaint.attachment && (
                            <div className="attachment-section mt-3">
                                <a 
                                    href={complaint.attachment} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-blue-500 hover:underline"
                                >
                                    View Attachment
                                </a>
                            </div>
                        )}
                    </div>
                ))}
            </div>
            
            {complaints.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                    No complaints found. Click "Log New Complaint" to submit your first complaint.
                </div>
            )}
        </div>
    );
};
```

---

## 💰 4. Log Payment and Attach Receipt

### **Log Payment with Receipt**
**POST** `/api/payments/payments/log_payment/`

**Description:** Log a payment made by the tenant with receipt attachment.

**Request (Form Data):**
```javascript
const formData = new FormData();
formData.append('amount', '500000');
formData.append('payment_method', 'Mobile Money');
formData.append('reference_number', 'TXN123456789');
formData.append('payment_for_month', '1');
formData.append('payment_for_year', '2024');
formData.append('due_date', '2024-01-31');
formData.append('receipt_file', fileObject);
formData.append('notes', 'Payment made via MTN Mobile Money');
```

**Request JSON Alternative:**
```json
{
    "amount": 500000,
    "payment_method": "Mobile Money",
    "reference_number": "TXN123456789",
    "payment_for_month": 1,
    "payment_for_year": 2024,
    "due_date": "2024-01-31",
    "notes": "Payment made via MTN Mobile Money"
}
```

**Response:**
```json
{
    "message": "Payment logged successfully. Property manager will verify and update status.",
    "payment": {
        "id": 25,
        "amount": "500000.00",
        "payment_method": "Mobile Money",
        "reference_number": "TXN123456789",
        "payment_for_month": 1,
        "payment_for_year": 2024,
        "due_date": "2024-01-31",
        "status": {
            "id": 3,
            "name": "Processing"
        },
        "receipt_file": "/media/payment_receipts/receipt_25.jpg",
        "notes": "Payment made via MTN Mobile Money",
        "created_at": "2024-01-26T16:30:00Z"
    }
}
```

**Frontend Implementation:**
```javascript
const PaymentLogger = () => {
    const [formData, setFormData] = useState({
        amount: '',
        payment_method: '',
        reference_number: '',
        payment_for_month: new Date().getMonth() + 1,
        payment_for_year: new Date().getFullYear(),
        due_date: '',
        receipt_file: null,
        notes: ''
    });
    const [loading, setLoading] = useState(false);

    const paymentMethods = [
        'Mobile Money',
        'Bank Transfer',
        'Cash',
        'Credit Card',
        'Debit Card',
        'Cheque'
    ];

    const months = [
        { value: 1, label: 'January' },
        { value: 2, label: 'February' },
        { value: 3, label: 'March' },
        { value: 4, label: 'April' },
        { value: 5, label: 'May' },
        { value: 6, label: 'June' },
        { value: 7, label: 'July' },
        { value: 8, label: 'August' },
        { value: 9, label: 'September' },
        { value: 10, label: 'October' },
        { value: 11, label: 'November' },
        { value: 12, label: 'December' }
    ];

    const handleSubmit = async (e) => {}

## 📊 Summary of Tenant APIs

### **Core Endpoints:**

1. **Rent Alerts:**
   - `GET /api/payments/payments/my_rent_alerts/`

2. **Payment Status:**
   - `GET /api/payments/payments/payment_receipt_status/`
   - `GET /api/payments/payments/my_payments/`

3. **Complaints:**
   - `GET /api/complaints/complaints/complaint_categories/`
   - `POST /api/complaints/complaints/log_complaint/`
   - `GET /api/complaints/complaints/my_complaints/`

4. **Payment Logging:**
   - `POST /api/payments/payments/log_payment/`

### **Authentication:**
All endpoints require JWT token in Authorization header.

### **File Uploads:**
- Complaint attachments: Images, PDFs
- Payment receipts: Images, PDFs, screenshots

### **Notifications:**
- SMS alerts for rent due dates (configured by property manager)
- Email/SMS confirmations for logged payments and complaints
- Real-time status updates on complaint progress

### **Mobile-Friendly:**
All components include responsive design with Tailwind CSS classes for mobile optimization.

---

## 🔧 Error Handling

### **Common Errors:**

**401 Unauthorized:**
```json
{
    "detail": "Given token not valid for any token type"
}
```

**404 Tenant Not Found:**
```json
{
    "error": "Tenant profile not found"
}
```

**400 Bad Request:**
```json
{
    "error": "Required field missing",
    "details": "Amount is required"
}
```

### **Frontend Error Handling:**
```javascript
const handleApiError = (response, data) => {
    if (response.status === 401) {
        // Redirect to login
        localStorage.removeItem('token');
        window.location.href = '/login';
    } else if (response.status === 404) {
        alert('Resource not found');
    } else {
        alert(data.error || 'An error occurred');
    }
};
```

---

This comprehensive guide provides everything needed to implement the Tenant frontend with all four core features: rent alerts, payment receipt status, complaint logging, and payment logging with receipt attachments! 🎉