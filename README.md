# User Authentication System

A lightweight threaded TCP authentication system with **email-based MFA** and device-bound tokens.

---

## Overview

This system provides secure user authentication using temporary passcodes, Base Tokens, and Master Tokens.  
Tokens are bound to the user’s **MAC address** and **IP**, ensuring only authorized devices can interact.

**Components:**
1. `op_creds.db` - stores user credentials and tokens.
2. `op_passcodes.db` - stores temporary passcodes.
3. TCP server:
   - **Identity Operator client thread** (`identity_operator_server.py`)
   - **Passcode Identity Operator client threader** (`passcode_identity_operator_server.py`)


## 1️⃣ User Requests Passcode

User sends a request to receive a temporary passcode via email:

require_passcode | MAC | Password | Phone | Email

Server workflow:

1. Check if email + password exists in `op_creds.db`.
2. Generate a **6-character temporary passcode**.
3. Store passcode in `op_passcodes.db` (expires in 3 minutes).
4. Send passcode to user email.

**Response example:**

Passcode is sent


## 2️⃣ User Authenticates with Passcode

User sends:

`MAC | Email | Phone | Password | Passcode`


Server validates:

- ✅ Passcode exists and matches
- ✅ Passcode is not expired

If valid:

1. Generate a **Base Token** (hashed credentials + salt)  
2. Generate a **Master Token** (bound to MAC + IP + Base Token)  
3. Store Master Token in `op_creds.db`  
4. Delete the used passcode  

**Response example:**

`pythonizer_<base_token>`


## 3️⃣ User Makes Requests Using Tokens

Each request includes:

`TOKEN | MAC | REQUEST | DATA...`

Server workflow:

1. Recreates Master Token from token + MAC + IP.
2. Fetches token from DB.
3. Checks expiry:

- Still valid → `"authorized"`
- Expired → `"renew|<new_base_token>"`
- Invalid → `"unauthorized"`

---

## 4️⃣ Token Renewal

If Master Token has expired:

1. Generate new Base Token from user credentials.
2. Replace old DB entry.
3. Return:

`renew|<base_token>`

**Purpose:** Ensure smooth workflow without re-login.


## 🔑 Key Features

- **MAC + IP Binding:** Tokens tied to user device and network.
- **Passcode Expiry:** Temporary codes expire in 3 minutes.
- **Token Expiry:** Master tokens expire after 1 hour and can be renewed.
- **Email-Based MFA:** Temporary passcodes sent via email.
- **Lightweight DB:** Uses SQLite (`op_creds.db`, `op_passcodes.db`).
- **Threaded TCP Servers:** Supports multiple users concurrently.

# 📂 Database Schema
## op_creds.db
`Column	Type`
`mac	TEXT`
`password	TEXT`
`email	TEXT`
`phone	TEXT`
`token	TEXT`
`expiry	TEXT`

## op_passcodes.db
`Column	Type`
`mac	TEXT`
`ip	TEXT`
`phone	TEXT`
`email	TEXT`
`passcode	TEXT`
`expiry	TEXT`
