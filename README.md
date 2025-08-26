# Tokenizer Authentication System

A **secure, token-based authentication system** for users, supporting **multi-factor authentication (MFA)** via temporary passcodes, token renewal, and device/IP binding.

---

## 📝 Project Overview

This system allows users to authenticate securely with:

- Temporary **passcodes** sent via email  
- **Base tokens** derived from credentials  
- **Master tokens** bound to MAC and IP  
- Automatic **token renewal** for expired sessions  

It uses **SQLite** for storage and **threaded TCP servers** for concurrent requests.

---

## 🎯 Purpose

- Verify user identity using **MFA passcodes**  
- Generate and manage session tokens tied to **MAC + IP**  
- Automatically **renew tokens** on expiration  
- Maintain **lightweight SQLite databases** for credentials and passcodes  
- Provide **threaded TCP servers** for simultaneous users  

---

## 🔄 High-Level Workflow

### 1️⃣ User Requests a Passcode
1. User sends their **MAC, email, password, and IP**.  
2. Server verifies credentials.  
3. Server generates a **6-character temporary passcode**.  
4. Passcode is stored in `op_passcodes.db` and emailed to the user.  

**Purpose:** Confirm the user's identity before issuing a token.

---

### 2️⃣ User Authenticates with Passcode
User sends:

```text
MAC | Email | Phone | Password | Passcode
