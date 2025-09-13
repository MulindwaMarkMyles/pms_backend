# Authentication & Login System - README

This document provides a comprehensive guide for implementing authentication and login functionality in the Property Management System.

## 🔐 Authentication Overview

The system uses **JWT (JSON Web Tokens)** for authentication with Django REST Framework Simple JWT. All users (Property Managers, Property Owners, Tenants) use the same authentication system but have different role-based access.

## Base URL
```
http://127.0.0.1:8000
```

---

## 📋 Available Authentication Endpoints

### **1. User Registration**
**POST** `/api/register/`

**Description:** Register a new user with profile and role assignment.

**Request JSON:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securePassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+256700123456",
    "address": "123 Main Street, Kampala",
    "role": "tenant"
}
```

**Roles Available:**
- `"owner"` - Property Owner
- `"manager"` - Property Manager  
- `"tenant"` - Tenant

**Response (201 Created):**
```json
{
    "message": "User and profile created successfully",
    "user": {
        "id": 5,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "profile": {
        "phone_number": "+256700123456",
        "address": "123 Main Street, Kampala",
        "role": "tenant"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### **2. User Login**
**POST** `/api/token/`

**Description:** Login with username/password to get JWT tokens.

**Request JSON:**
```json
{
    "username": "john_doe",
    "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **3. Token Refresh**
**POST** `/api/token/refresh/`

**Description:** Get a new access token using refresh token.

**Request JSON:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **4. Get User Profile**
**GET** `/api/profile/`

**Description:** Get current user's profile information.

**Headers Required:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response (200 OK):**
```json
{
    "id": 5,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+256700123456",
    "address": "123 Main Street, Kampala",
    "role": "tenant",
    "created_at": "2024-01-26T10:30:00Z"
}
```

---

## 🔄 Token Lifecycle

### **Access Token:**
- **Lifetime:** 60 minutes (configurable)
- **Usage:** Include in Authorization header for API requests
- **Purpose:** Authenticate API calls

### **Refresh Token:**
- **Lifetime:** 24 hours (configurable)
- **Usage:** Get new access tokens when they expire
- **Purpose:** Maintain user sessions

### **Token Flow:**
1. User logs in → Gets access + refresh tokens
2. Use access token for API calls
3. When access token expires → Use refresh token to get new access token
4. When refresh token expires → User must login again

---

## 🚀 Frontend Implementation

### **1. Login Component**

```javascript
import React, { useState } from 'react';

const Login = () => {
    const [credentials, setCredentials] = useState({
        username: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch('/api/token/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            if (response.ok) {
                const data = await response.json();
                
                // Store tokens
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                
                // Get user profile to determine role
                const profileResponse = await fetch('/api/profile/', {
                    headers: {
                        'Authorization': `Bearer ${data.access}`
                    }
                });
                
                if (profileResponse.ok) {
                    const profile = await profileResponse.json();
                    localStorage.setItem('user_profile', JSON.stringify(profile));
                    
                    // Redirect based on role
                    switch(profile.role) {
                        case 'owner':
                            window.location.href = '/owner-dashboard';
                            break;
                        case 'manager':
                            window.location.href = '/manager-dashboard';
                            break;
                        case 'tenant':
                            window.location.href = '/tenant-dashboard';
                            break;
                        default:
                            window.location.href = '/dashboard';
                    }
                } else {
                    setError('Failed to get user profile');
                }
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Login failed');
            }
        } catch (error) {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
            
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}
            
            <form onSubmit={handleLogin} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium mb-1">Username</label>
                    <input
                        type="text"
                        value={credentials.username}
                        onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                        required
                        className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter your username"
                    />
                </div>
                
                <div>
                    <label className="block text-sm font-medium mb-1">Password</label>
                    <input
                        type="password"
                        value={credentials.password}
                        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                        required
                        className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter your password"
                    />
                </div>
                
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50"
                >
                    {loading ? 'Logging in...' : 'Login'}
                </button>
            </form>
            
            <div className="mt-4 text-center">
                <a href="/register" className="text-blue-500 hover:underline">
                    Don't have an account? Register here
                </a>
            </div>
        </div>
    );
};

export default Login;
```

### **2. Registration Component**

```javascript
import React, { useState } from 'react';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        address: '',
        role: 'tenant'
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const response = await fetch('/api/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const data = await response.json();
                
                // Store tokens (user is automatically logged in)
                localStorage.setItem('access_token', data.tokens.access);
                localStorage.setItem('refresh_token', data.tokens.refresh);
                localStorage.setItem('user_profile', JSON.stringify({
                    ...data.user,
                    ...data.profile
                }));
                
                setSuccess('Registration successful! Redirecting...');
                
                // Redirect based on role
                setTimeout(() => {
                    switch(formData.role) {
                        case 'owner':
                            window.location.href = '/owner-dashboard';
                            break;
                        case 'manager':
                            window.location.href = '/manager-dashboard';
                            break;
                        case 'tenant':
                            window.location.href = '/tenant-dashboard';
                            break;
                        default:
                            window.location.href = '/dashboard';
                    }
                }, 2000);
            } else {
                const errorData = await response.json();
                setError(errorData.error || 'Registration failed');
            }
        } catch (error) {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-container max-w-2xl mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-6 text-center">Register</h2>
            
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}
            
            {success && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                    {success}
                </div>
            )}
            
            <form onSubmit={handleRegister} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">Username *</label>
                        <input
                            type="text"
                            value={formData.username}
                            onChange={(e) => setFormData({...formData, username: e.target.value})}
                            required
                            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium mb-1">Email *</label>
                        <input
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData({...formData, email: e.target.value})}
                            required
                            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>
                
                <div>
                    <label className="block text-sm font-medium mb-1">Password *</label>
                    <input
                        type="password"
                        value={formData.password}
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                        required
                        className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">First Name</label>
                        <input
                            type="text"
                            value={formData.first_name}
                            onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium mb-1">Last Name</label>
                        <input
                            type="text"
                            value={formData.last_name}
                            onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>
                
                <div>
                    <label className="block text-sm font-medium mb-1">Phone Number</label>
                    <input
                        type="tel"
                        value={formData.phone_number}
                        onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                        className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="+256700123456"
                    />
                </div>
                
                <div>
                    <label className="block text-sm font-medium mb-1">Address</label>
                    <textarea
                        value={formData.address}
                        onChange={(e) => setFormData({...formData, address: e.target.value})}
                        className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows="2"
                    />
                </div>
                
                <div>
                    <label className="block text-sm font-medium mb-1">Role *</label>
                    <select
                        value={formData.role}
                        onChange={(e) => setFormData({...formData, role: e.target.value})}
                        required
                        className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="tenant">Tenant</option>
                        <option value="manager">Property Manager</option>
                        <option value="owner">Property Owner</option>
                    </select>
                </div>
                
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50"
                >
                    {loading ? 'Registering...' : 'Register'}
                </button>
            </form>
            
            <div className="mt-4 text-center">
                <a href="/login" className="text-blue-500 hover:underline">
                    Already have an account? Login here
                </a>
            </div>
        </div>
    );
};

export default Register;
```

### **3. API Helper Functions**

```javascript
// api.js - Utility functions for handling authentication

// Get stored token
export const getAccessToken = () => {
    return localStorage.getItem('access_token');
};

export const getRefreshToken = () => {
    return localStorage.getItem('refresh_token');
};

// Get user profile
export const getUserProfile = () => {
    const profile = localStorage.getItem('user_profile');
    return profile ? JSON.parse(profile) : null;
};

// Check if user is authenticated
export const isAuthenticated = () => {
    return !!getAccessToken();
};

// Logout user
export const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_profile');
    window.location.href = '/login';
};

// Refresh access token
export const refreshAccessToken = async () => {
    const refreshToken = getRefreshToken();
    
    if (!refreshToken) {
        logout();
        return null;
    }

    try {
        const response = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh: refreshToken
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return data.access;
        } else {
            logout();
            return null;
        }
    } catch (error) {
        logout();
        return null;
    }
};

// API request with automatic token refresh
export const apiRequest = async (url, options = {}) => {
    let token = getAccessToken();
    
    if (!token) {
        logout();
        return null;
    }

    // Add Authorization header
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    let response = await fetch(url, {
        ...options,
        headers
    });

    // If token expired, try to refresh
    if (response.status === 401) {
        token = await refreshAccessToken();
        
        if (token) {
            // Retry request with new token
            response = await fetch(url, {
                ...options,
                headers: {
                    ...headers,
                    'Authorization': `Bearer ${token}`
                }
            });
        }
    }

    return response;
};

// Usage example:
// const response = await apiRequest('/api/payments/payments/my_payments/');
// const data = await response.json();
```

### **4. Authentication Guard Component**

```javascript
// AuthGuard.js - Protect routes that require authentication

import React, { useEffect, useState } from 'react';
import { isAuthenticated, getUserProfile } from './api';

const AuthGuard = ({ children, requiredRole = null }) => {
    const [loading, setLoading] = useState(true);
    const [authorized, setAuthorized] = useState(false);

    useEffect(() => {
        const checkAuth = () => {
            if (!isAuthenticated()) {
                window.location.href = '/login';
                return;
            }

            if (requiredRole) {
                const profile = getUserProfile();
                if (!profile || profile.role !== requiredRole) {
                    window.location.href = '/unauthorized';
                    return;
                }
            }

            setAuthorized(true);
            setLoading(false);
        };

        checkAuth();
    }, [requiredRole]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg">Loading...</div>
            </div>
        );
    }

    if (!authorized) {
        return null;
    }

    return children;
};

// Usage examples:
// <AuthGuard>
//     <Dashboard />
// </AuthGuard>

// <AuthGuard requiredRole="owner">
//     <OwnerDashboard />
// </AuthGuard>

export default AuthGuard;
```

---

## 🛡️ Role-Based Access Control

### **User Roles & Permissions:**

#### **Property Owner (`"owner"`):**
- Full access to all estates, payments, and reports
- Dashboard analytics and alerts
- Property management oversight

#### **Property Manager (`"manager"`):**
- Manage tenants, apartments, complaints
- Update payment statuses
- Handle maintenance requests

#### **Tenant (`"tenant"`):**
- View own payments and complaints
- Log payments and complaints
- Receive rent alerts

### **Role Checking Example:**
```javascript
const checkUserRole = () => {
    const profile = getUserProfile();
    
    if (profile) {
        switch(profile.role) {
            case 'owner':
                return 'Property Owner';
            case 'manager':
                return 'Property Manager';
            case 'tenant':
                return 'Tenant';
            default:
                return 'Unknown';
        }
    }
    return null;
};
```

---

## 🔧 Error Handling

### **Common Authentication Errors:**

**Invalid Credentials (401):**
```json
{
    "detail": "No active account found with the given credentials"
}
```

**Token Expired (401):**
```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}
```

**Validation Errors (400):**
```json
{
    "error": "Username already exists"
}
```

---

## ⚙️ Configuration

### **JWT Settings (Django settings.py):**
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### **CORS Settings (for frontend):**
```python
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]
```

---

## 🚀 Testing Authentication

### **Manual Testing with cURL:**

**Register User:**
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "role": "tenant"
  }'
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**Protected Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## 📱 Mobile App Considerations

### **Token Storage:**
- Use secure storage (Keychain on iOS, Keystore on Android)
- Never store tokens in plain text

### **Biometric Authentication:**
- Store refresh token securely
- Use biometrics to unlock access token
- Implement automatic re-authentication

### **Offline Support:**
- Cache user profile locally
- Queue API requests when offline
- Sync when connection restored

---

This comprehensive authentication system provides secure, role-based access for all user types in the Property Management System! 🔐