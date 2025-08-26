🔹 Project Explanation: Tokenizer Authentication System
1️⃣ Purpose

This project provides a secure, token-based authentication system for operators. Its main goals are:

Verify operator identity using multi-factor authentication (MFA) via passcodes.

Generate and manage session tokens that are bound to the operator’s MAC address and IP.

Renew tokens automatically when they are expired, without asking the operator to re-login.

Maintain a simple, lightweight database for credentials and passcodes using SQLite.

Enable secure communication between the client and server via custom TCP sockets.

This system is useful in environments where operators need controlled access, and you want fine-grained token validation.

2️⃣ High-Level Workflow
Step 1: Operator Requests a Passcode

The operator sends a request to the server with their email, password, MAC, and IP.

Server verifies that the email/password exists.

Server generates a temporary 6-character passcode.

Passcode is stored in op_passcodes.db and emailed to the operator.

Purpose: Ensure that the operator requesting access is the rightful owner of the account.

Step 2: Operator Authenticates with Passcode

Operator sends MAC | Email | Phone | Password | Passcode to the server.

Server validates:

Passcode exists in DB

Passcode matches input

Passcode is not expired

If valid:

Server generates a Base Token (hashed credentials + salt)

Server generates a Master Token (bound to MAC + IP + Base Token)

Stores Master Token in op_creds.db

Deletes the used passcode from DB

Response to operator:

𝔄𝔴𝔣𝔢𝔯_𝔥𝔢𝔩𝔩𝔴𝔞𝔩𝔩_<base_token>


Purpose: Multi-factor authentication ensures secure operator login and prevents unauthorized access.

Step 3: Operator Makes Requests Using Tokens

Every subsequent request includes:

TOKEN | MAC | REQUEST | DATA...


Server validates token:

Recreates Master Token from received token + MAC + IP

Fetches stored token from DB

Checks token expiry:

Still valid → "authorized"

Expired → generates new base token, replaces DB entry → "renew|<new_base_token>"

Invalid or tampered → "unauthorized"

Purpose: Operators can continue working without re-login while maintaining session security.

Step 4: Token Renewal

If the Master Token has expired, the server:

Generates a new Base Token from the operator’s credentials

Replaces the old DB entry

Returns "renew|<base_token>" to the operator

Operator seamlessly continues operations with the new token.

Purpose: Ensure smooth workflow without compromising security.

3️⃣ Key Features

MAC + IP Binding: Tokens are bound to the operator’s device and network.

Passcode Expiry: Temporary codes expire after 3 minutes to prevent replay attacks.

Token Expiry: Master tokens expire after 1 hour and are renewable.

Email-Based MFA: Temporary passcodes are sent via email.

Lightweight DB: Uses SQLite (op_creds.db, op_passcodes.db) for storage.

Threaded TCP Servers: Supports concurrent operator authentication and passcode requests.
