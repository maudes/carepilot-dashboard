# CarePilot diagrams (Phase 2 design)

Status: draft for review. These describe the Phase 2 target, not what is implemented today.
Phase 1 is the existing flow. Phase 2 is what is new.

The overall block diagram is a separate file: [architecture.svg](architecture.svg).

![CarePilot architecture](architecture.svg)

Contents

1. [Swimlane: login, daily record, export](#1-swimlane-login-daily-record-export)
2. [Swimlane: email OTP login (Phase 1)](#2-swimlane-email-otp-login-phase-1)
3. [Swimlane: encrypted vault unlock](#3-swimlane-encrypted-vault-unlock)
4. [Swimlane: export OTP failure paths](#4-swimlane-export-otp-failure-paths)
5. [Flow: first-run setup wizard](#5-flow-first-run-setup-wizard)
6. [Structure: settings page and verification tiers](#6-structure-settings-page-and-verification-tiers)

---

## 1. Swimlane: login, daily record, export

Purple blocks are new in Phase 2, green is the existing Phase 1 flow. The three parts below are steps in one session and are not project phases. SMTP and Inbox are separate lanes on purpose: the OTP leaves the system through SMTP and only then reaches the user.

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant S as Streamlit
    participant F as FastAPI
    participant D as Storage
    participant M as SMTP
    participant I as Inbox

    rect rgb(238, 237, 254)
    Note over U,I: Part 1 - Login (passphrase shown, Phase 2)
    U->>S: Passphrase
    S->>F: POST login
    F->>D: Check hash
    F-->>S: Access token
    end

    rect rgb(225, 245, 238)
    Note over U,I: Part 2 - Daily record (Phase 1)
    U->>S: Daily data
    S->>F: POST record
    F->>D: Save record
    end

    rect rgb(238, 237, 254)
    Note over U,I: Part 3 - Export with email OTP (Phase 2)
    U->>S: Click export
    S->>F: Request export
    F->>M: Send OTP
    M->>I: Deliver
    I-->>U: Read code
    U->>S: Enter code
    S->>F: Verify code
    F->>D: Check OTP, read data
    F-->>S: JSON or FHIR
    S-->>U: Download file
    end
```

---

## 2. Swimlane: email OTP login (Phase 1)

The existing flow: `login-request` returns an OTP token, `verify` takes the token plus the code and returns the access token.

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant S as Streamlit
    participant F as FastAPI
    participant D as Storage
    participant M as SMTP
    participant I as Inbox

    U->>S: Enter email
    S->>F: Login request
    F->>D: Store OTP
    F->>M: Send OTP
    M->>I: Deliver
    F-->>S: OTP token
    I-->>U: Read code
    U->>S: Enter code
    S->>F: Token + code
    F->>D: Check OTP
    F-->>S: Access token
```

Compare with the passphrase login in diagram 1: four steps, no SMTP, no network needed.

---

## 3. Swimlane: encrypted vault unlock

Applies when data storage is SQLite + SQLCipher. The service starts locked. A wrong passphrase fails at the read test, because the key is derived from the passphrase. No password hash is stored for verification.

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant S as Streamlit
    participant F as FastAPI
    participant E as Encrypted file

    rect rgb(238, 237, 254)
    Note over U,E: Part 1 - Start, vault is locked
    U->>S: Open app
    S->>F: Check status
    F-->>S: Vault locked
    end

    rect rgb(238, 237, 254)
    Note over U,E: Part 2 - Unlock with passphrase
    U->>S: Passphrase
    S->>F: POST unlock
    Note over F: Argon2id derives the key
    F->>E: Key + test read
    E-->>F: Read OK
    F-->>S: Unlocked, token
    end

    rect rgb(250, 236, 231)
    Note over U,E: Part 3 - Alt, wrong passphrase
    U->>S: Wrong passphrase
    S->>F: POST unlock
    F->>E: Key + test read
    E-->>F: Read fails
    F-->>S: Wrong, wait longer
    S-->>U: Retry after wait
    end
```

---

## 4. Swimlane: export OTP failure paths

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant S as Streamlit
    participant F as FastAPI
    participant D as Storage

    alt Wrong code, attempts left
        U->>S: Enter code
        S->>F: Verify code
        F->>D: Count attempt
        F-->>S: Invalid, 2 left
    else Code expired after 5 minutes
        S->>F: Verify code
        F->>D: Look up OTP
        D-->>F: Not found
        F-->>S: Expired, resend
    else Third failure
        F->>D: Lock 30 min
        F-->>S: Locked
        S-->>U: Try later
    end
```

The numbers (5 minutes, 3 tries, 30 minute lock) are proposed defaults, not final.

---

## 5. Flow: first-run setup wizard

```mermaid
flowchart TD
    A["1. Setup code<br/>localhost only"] --> B["2. Data location<br/>this device or shared"]
    B --> C["3. Pick a preset<br/>local, cloud, mix, advanced"]
    C --> D["4. Unlock secret<br/>passphrase + recovery key"]
    D --> E["5. Verify email<br/>OTP, required"]
    E --> F["6. Run tests<br/>SMTP, database"]
    F --> G["7. Lock setup<br/>close the setup API"]

    classDef v2 fill:#EEEDFE,stroke:#534AB7,color:#3C3489
    class A,B,C,D,E,F,G v2
```

Presets

| Preset | Login | Token store | Data storage |
|---|---|---|---|
| Local vault | Passphrase | LocalKV | SQLite + SQLCipher |
| Cloud connected (the Phase 1 setup) | Email OTP | Upstash | Postgres |
| Hybrid | Passphrase + Email OTP | LocalKV | SQLite (encryption optional) |
| Advanced | pick each | pick each | pick each |

Rules: choosing encrypted storage forces passphrase login, because Email OTP cannot derive the key. Every preset requires a verified email. Setup binds to localhost only and needs a one-time code printed by the server, then the setup API closes.

---

## 6. Structure: settings page and verification tiers

```mermaid
flowchart TB
    subgraph Settings["Settings page"]
        direction LR
        L["Login methods<br/>add or remove"]:::pass
        P["Passphrase<br/>change, new key"]:::pass
        E["Email and SMTP<br/>old and new verified"]:::otp
        T["Token store<br/>switch, signs out"]:::sess
        S["Data storage<br/>switch, encrypt"]:::otp
        X["Export and import<br/>JSON or FHIR"]:::otp
    end

    classDef otp fill:#FAECE7,stroke:#993C1D,color:#712B13
    classDef pass fill:#E1F5EE,stroke:#0F6E56,color:#085041
    classDef sess fill:#F1EFE8,stroke:#5F5E5A,color:#444441
```

| Colour | Verification needed | Sections |
|---|---|---|
| Orange | Email OTP | Email and SMTP, data storage, export and import |
| Green | Current passphrase | Login methods, passphrase |
| Grey | Active session only | Token store |

Where no passphrase exists (email-only setup), the "current passphrase" tier falls back to Email OTP.
