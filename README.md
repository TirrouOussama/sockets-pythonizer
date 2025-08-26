# User Authentication & Tokenizer System

A secure, token-based authentication system for users, supporting multi-factor authentication (MFA) via temporary passcodes, token renewal, and device/IP binding.

---

## Project Overview

This system allows users to authenticate securely with:

- Temporary passcodes sent via email  
- Base tokens derived from credentials  
- Master tokens bound to MAC and IP  
- Automatic token renewal for expired sessions  

It uses SQLite for storage and threaded TCP servers for concurrent requests.

---

## Purpose

- Verify user identity using MFA passcodes  
- Generate and manage session tokens tied to MAC + IP  
- Automatically renew tokens on expiration  
- Maintain lightweight SQLite databases for credentials and passcodes  
- Provide threaded TCP servers for simultaneous users  

---

## Workflow

### 1. User Requests a Passcode

1. User sends their MAC, email, password, and IP.  
2. Server verifies credentials.  
3. Server generates a 6-character temporary passcode.  
4. Passcode is stored in `op_passcodes.db` and emailed to the user.  

### 2. User Authenticates with Passcode

User sends:

```text
MAC | Email | Phone | Password | Passcode
Server validates:

Passcode exists and matches

Passcode is not expired

If valid:

Generate a Base Token (hashed credentials + salt)

Generate a Master Token (bound to MAC + IP + Base Token)

Store Master Token in op_creds.db

Delete the used passcode

Response example:

text
Copy
Edit
Awfer_hellwall_<base_token>
3. User Makes Requests Using Tokens
Each request includes:

text
Copy
Edit
TOKEN | MAC | REQUEST | DATA...
Server checks:

Recreates Master Token from token + MAC + IP

Fetches token from DB

Checks expiry:

text
Copy
Edit
Still valid   → "authorized"
Expired       → "renew|<new_base_token>"
Invalid       → "unauthorized"
4. Token Renewal
If Master Token has expired:

Generate new Base Token from user credentials

Replace old DB entry

Return:

text
Copy
Edit
renew|<base_token>
Purpose: Ensure smooth workflow without requiring the user to re-login.

Key Features
MAC + IP Binding: Tokens tied to user device and network

Passcode Expiry: Temporary codes expire in 3 minutes

Token Expiry: Master tokens expire after 1 hour and can be renewed

Email-Based MFA: Temporary passcodes sent via email

Lightweight DB: Uses SQLite (op_creds.db, op_passcodes.db)

Threaded TCP Servers: Supports multiple users concurrently
