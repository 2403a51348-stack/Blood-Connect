# BloodConnect: Comprehensive Software Requirements Specification (SRS) & System Architecture Diagrams

---

## 1. Software Requirements Specification (SRS)

### 1.1 Introduction
The **BloodConnect** web application is an emergency healthcare blood coordination system designed to discover and connect voluntary blood donors with patients in urgent clinical need.

### 1.2 User Classes and Characteristics
1. **Voluntary Blood Donors:** Adults aged 18-65 capable of donating blood, who register their blood group and update their availability status.
2. **Blood Requesters (Patients, Attendants, Hospitals):** Individuals or medical institutions in immediate need of blood units for surgeries or emergencies.
3. **Hospital Administrators:** Medical supervisors who monitor platform metrics, review requests, and safeguard system integrity.

### 1.3 Functional Requirements
- **FR-1 (Registration & Auth):** Users must be able to register as Donors or Requesters with input validation, duplicate email/username checking, and password strength validation.
- **FR-2 (Donor Availability):** Donors must be able to toggle their status between Available and Unavailable instantly.
- **FR-3 (Blood Request Creation):** Requesters must be able to submit emergency requests with patient name, required blood group, units, hospital address, city, and urgency level.
- **FR-4 (Compatibility-Based Matching):** System must evaluate red blood cell transfusion compatibility (ABO and Rh factor rules) and rank donors using a 100-point multi-factor score.
- **FR-5 (In-App Notifications):** System must dispatch real-time in-app alerts when requests are created, when donors are contacted, and when responses (Accept/Decline) are submitted.
- **FR-6 (Tracking & Timeline):** Requesters must be able to track request progression from Created &rarr; Contacted &rarr; Accepted &rarr; Hospital Verification &rarr; Fulfilled.
- **FR-7 (Admin Control):** Administrators must be able to view system metrics, blood distribution, manage user accounts, and review audit logs.

### 1.4 Non-Functional Requirements
- **NFR-1 (Performance):** Donor matching calculation must execute in under 1 second for active regional donor pools.
- **NFR-2 (Privacy):** Donor telephone numbers and personal addresses must remain masked until a donor explicitly accepts a request.
- **NFR-3 (Compatibility):** 100% responsive design across Desktop, Tablet, and Mobile browsers using Bootstrap 5.

---

## 2. System Architecture Diagram

```mermaid
flowchart TD
    Client["Client Browser (HTML5 / Bootstrap 5 / JS)"]

    subgraph Django Application Server
        Router["URL Dispatcher (bloodconnect/urls.py)"]
        Middleware["Security & Auth Middleware"]
        
        subgraph Apps
            AccountsApp["accounts (User & Profiles)"]
            DonorsApp["donors (Donor Profiles & History)"]
            RequestsApp["requests_app (Blood Requests & Tracking)"]
            MatchingApp["matching (Algorithm & Response Engine)"]
            NotifApp["notifications (In-App Alert Queue)"]
            DashboardApp["dashboard (Admin Metrics & Audit Logs)"]
        end

        ORM["Django ORM"]
    end

    subgraph Persistence Layer
        MySQL[("MySQL 8.0 Database (bloodconnect_db)")]
    end

    Client <-->|HTTP / HTTPS| Router
    Router --> Middleware
    Middleware --> AccountsApp
    Middleware --> DonorsApp
    Middleware --> RequestsApp
    Middleware --> MatchingApp
    Middleware --> NotifApp
    Middleware --> DashboardApp

    AccountsApp --> ORM
    DonorsApp --> ORM
    RequestsApp --> ORM
    MatchingApp --> ORM
    NotifApp --> ORM
    DashboardApp --> ORM

    ORM <-->|PyMySQL / TCP 3306| MySQL
```

---

## 3. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USER ||--o| USER_PROFILE : "has"
    USER ||--o| DONOR_PROFILE : "registers as"
    USER ||--o| REQUESTER_PROFILE : "registers as"
    USER ||--o{ BLOOD_REQUEST : "submits"
    USER ||--o{ NOTIFICATION : "receives"
    USER ||--o{ ADMIN_ACTIVITY_LOG : "executes"

    DONOR_PROFILE ||--o{ DONOR_MATCH : "matched in"
    DONOR_PROFILE ||--o{ DONATION_RESPONSE : "provides"
    DONOR_PROFILE ||--o{ DONATION_HISTORY : "logs"

    BLOOD_REQUEST ||--o{ DONOR_MATCH : "produces"
    BLOOD_REQUEST ||--o{ DONATION_RESPONSE : "receives"
    BLOOD_REQUEST ||--o{ DONATION_HISTORY : "fulfills"

    USER {
        int id PK
        string username UK
        string email UK
        string first_name
        string last_name
        string password
        boolean is_active
        boolean is_staff
    }

    USER_PROFILE {
        int id PK
        int user_id FK
        string role "DONOR, REQUESTER, ADMIN"
        string phone
        string city
        string state
        text address
        boolean is_verified
    }

    DONOR_PROFILE {
        int id PK
        int user_id FK
        string blood_group "A+, A-, B+, B-, AB+, AB-, O+, O-"
        string phone
        string city
        string state
        text address
        boolean is_available
        int total_donations
        date last_donation_date
        datetime availability_updated_at
    }

    REQUESTER_PROFILE {
        int id PK
        int user_id FK
        string phone
        string city
        string state
        text address
        string organization_name
    }

    BLOOD_REQUEST {
        int id PK
        string request_id UK
        int requester_id FK
        string patient_name
        string blood_group
        int units_required
        string hospital_name
        text hospital_address
        string city
        string state
        string urgency "LOW, MEDIUM, HIGH, CRITICAL"
        string status "PENDING, DONOR_CONTACTED, ACCEPTED, REJECTED, IN_PROGRESS, COMPLETED, CANCELLED"
        datetime created_at
    }

    DONOR_MATCH {
        int id PK
        int blood_request_id FK
        int donor_id FK
        int match_score
        text match_reasons
        string status "SUGGESTED, CONTACTED, ACCEPTED, DECLINED"
        datetime contacted_at
        datetime responded_at
    }

    DONATION_RESPONSE {
        int id PK
        int donor_match_id FK
        int donor_id FK
        int blood_request_id FK
        string response "ACCEPTED, DECLINED"
        text remarks
        datetime responded_at
    }

    NOTIFICATION {
        int id PK
        int recipient_id FK
        string title
        text message
        string notification_type
        boolean is_read
        string related_url
        datetime created_at
    }

    DONATION_HISTORY {
        int id PK
        int donor_id FK
        int blood_request_id FK
        date donation_date
        int units_donated
        string hospital_name
        boolean verified_by_hospital
    }

    ADMIN_ACTIVITY_LOG {
        int id PK
        int admin_user_id FK
        string action_type
        text description
        string target_model
        string target_id
        datetime timestamp
    }
```

---

## 4. Class Diagram

```mermaid
classDiagram
    class User {
        +int id
        +String username
        +String email
        +set_password(raw_pass)
        +check_password(raw_pass)
    }

    class DonorProfile {
        +String blood_group
        +String phone
        +String city
        +String state
        +Boolean is_available
        +int total_donations
        +Date last_donation_date
        +toggle_availability()
    }

    class RequesterProfile {
        +String phone
        +String city
        +String organization_name
    }

    class BloodRequest {
        +String request_id
        +String patient_name
        +String blood_group
        +int units_required
        +String hospital_name
        +String urgency
        +String status
        +save()
    }

    class DonorMatch {
        +int match_score
        +String match_reasons
        +String status
        +contacted_at
        +responded_at
    }

    class MatchingService {
        +evaluate_donor_match(request, donor)
        +find_and_rank_matching_donors(request)
        +contact_matched_donor(request, donor)
    }

    class Notification {
        +String title
        +String message
        +Boolean is_read
        +mark_as_read()
    }

    User "1" --> "1" DonorProfile : donor_profile
    User "1" --> "1" RequesterProfile : requester_profile
    User "1" --> "*" BloodRequest : blood_requests
    User "1" --> "*" Notification : notifications
    BloodRequest "1" --> "*" DonorMatch : matches
    DonorProfile "1" --> "*" DonorMatch : matches
    MatchingService ..> BloodRequest : evaluates
    MatchingService ..> DonorProfile : ranks
```

---

## 5. Use Case Diagram

```mermaid
flowchart LR
    Donor(("Voluntary Donor"))
    Requester(("Patient / Requester"))
    Admin(("Administrator"))

    subgraph BloodConnect Platform
        UC1["Register & Authenticate"]
        UC2["Toggle Availability"]
        UC3["Create Blood Request"]
        UC4["Calculate Donor Matches"]
        UC5["Contact Matched Donors"]
        UC6["Accept / Decline Request"]
        UC7["Track Fulfillment Timeline"]
        UC8["Manage Notifications"]
        UC9["Audit Logs & Deactivate Accounts"]
    end

    Donor --> UC1
    Donor --> UC2
    Donor --> UC6
    Donor --> UC8

    Requester --> UC1
    Requester --> UC3
    Requester --> UC4
    Requester --> UC5
    Requester --> UC7
    Requester --> UC8

    Admin --> UC1
    Admin --> UC7
    Admin --> UC9
    Admin --> UC8
```

---

## 6. Sequence Diagram: Emergency Blood Request & Donor Acceptance

```mermaid
sequenceDiagram
    autonumber
    actor R as Requester
    participant Web as Web UI / Views
    participant Svc as Matching Service
    participant DB as MySQL Database
    participant Notif as Notification Engine
    actor D as Donor

    R->>Web: Submit Emergency Blood Request (e.g. O+, 2 Units, NIMS Hospital)
    Web->>DB: Save BloodRequest (Status = PENDING)
    Web->>Svc: find_and_rank_matching_donors(blood_request)
    Svc->>DB: Query compatible active donors (O-, O+)
    Svc->>Svc: Calculate 100-pt score (Blood compatibility, City, Availability)
    Svc->>DB: Store DonorMatch records with scores
    Web-->>R: Display Ranked Matching Donors Page
    
    R->>Web: Click "Send Request" to Donor
    Web->>Svc: contact_matched_donor(blood_request, donor)
    Svc->>DB: Update DonorMatch (Status = CONTACTED)
    Svc->>DB: Update BloodRequest (Status = DONOR_CONTACTED)
    Svc->>Notif: create_notification(donor, "Urgent Blood Request O+")
    Notif->>DB: Insert Notification Record
    
    D->>Web: Views Donor Dashboard & Notification
    D->>Web: Clicks "Accept - Ready to Donate"
    Web->>DB: Update DonorMatch (Status = ACCEPTED)
    Web->>DB: Update BloodRequest (Status = ACCEPTED)
    Web->>Notif: create_notification(requester, "Donor Accepted! Contact: +91 98765...")
    Web-->>R: Live Tracking updates: Donor phone revealed for clinical arrival
```

---

## 7. Data Flow Diagram (DFD)

### Level 0 DFD (Context Diagram)
```mermaid
flowchart LR
    Donor["Voluntary Donor"]
    Requester["Patient / Hospital"]
    Admin["Hospital Admin"]
    System["BloodConnect Platform"]

    Donor <-->|Registration, Availability, Responses| System
    Requester <-->|Blood Need Details, Donor Contacting| System
    Admin <-->|Audit Logs, Account Governance, Reports| System
```

### Level 1 DFD (Decomposed Processes)
```mermaid
flowchart TD
    D["Donor"]
    R["Requester"]
    
    P1["1.0 Authentication & Profile Management"]
    P2["2.0 Blood Request Processing"]
    P3["3.0 Matching & Scoring Engine"]
    P4["4.0 Notification & Response Coordination"]
    P5["5.0 Administrative Audit & Governance"]

    D1[("Users & Profiles Store")]
    D2[("Blood Requests Store")]
    D3[("Matches & Responses Store")]
    D4[("Notifications Store")]
    D5[("Activity Logs Store")]

    D -->|Credentials & Profile| P1
    R -->|Credentials & Profile| P1
    P1 <--> D1

    R -->|Patient & Blood Details| P2
    P2 -->|Save Request| D2
    P2 -->|Initiate Discovery| P3

    P3 <-->|Read Donors| D1
    P3 <-->|Read Request| D2
    P3 -->|Store Ranked Matches| D3

    R -->|Contact Donor Action| P4
    D -->|Accept / Decline Decision| P4
    P4 <--> D3
    P4 -->|Dispatch Alerts| D4
    P4 -->|Update Status| D2

    P5 <--> D1
    P5 <--> D2
    P5 <--> D5
```

---

## 8. Activity Diagram: Blood Request Lifecycle

```mermaid
flowchart TD
    Start([Requester Needs Emergency Blood]) --> Form[Fill Blood Request Form]
    Form --> Valid{Valid Inputs?}
    Valid -- No --> FixErrors[Display Validation Warnings] --> Form
    Valid -- Yes --> SaveReq[Save BloodRequest into Database]
    SaveReq --> RunAlgo[Execute Multi-Factor Matching Algorithm]
    RunAlgo --> Rank[Rank Donors by Compatibility & Proximity]
    Rank --> DisplayMatches[Display Ranked Donors Results Page]
    DisplayMatches --> Outreach{Choose Action}
    Outreach -- Target Specific Donor --> ContactOne[Send Request to Selected Donor]
    Outreach -- Broadcast --> ContactAll[Broadcast to All Available Donors]
    ContactOne --> Alert[Dispatch In-App Notifications to Donors]
    ContactAll --> Alert
    Alert --> DonorDecision{Donor Decision}
    DonorDecision -- Decline --> RecDecline[Record Declined Status & Notify Requester]
    DonorDecision -- Accept --> RecAccept[Update Request to ACCEPTED & Reveal Donor Phone]
    RecAccept --> Hospital[Donor Arrives at Hospital Blood Bank]
    Hospital --> ClinicalVerify[Hospital Conducts Mandatory Clinical Cross-Matching]
    ClinicalVerify --> Transfusion[Transfusion Completed]
    Transfusion --> MarkComplete[Requester / Admin Marks Request as COMPLETED]
    MarkComplete --> End([Request Lifecycle Terminated])
```

---

## 9. Testing & Quality Assurance Documentation

The application includes 15 automated test cases covering end-to-end functionality:
1. `test_donor_registration_success`: Validates User, UserProfile, and DonorProfile atomic creation.
2. `test_requester_registration_success`: Validates RequesterProfile creation.
3. `test_duplicate_username_prevented`: Confirms unique username database validation.
4. `test_login_and_logout`: Confirms session creation and role-based redirect logic.
5. `test_donor_dashboard_accessible`: Verifies authenticated donor dashboard rendering.
6. `test_toggle_availability`: Tests instantaneous toggle between Available & Unavailable.
7. `test_add_donation_history`: Tests voluntary donation history recording and stats update.
8. `test_create_blood_request`: Tests emergency blood request generation and unique ID formatting (`REQ-YYYYMMDD-XXXXXX`).
9. `test_cancel_blood_request`: Tests requester authorization to cancel active blood requests.
10. `test_transfusion_compatibility_rules`: Validates O- universal donor and AB+ universal recipient rules across all 8 ABO/Rh blood groups.
11. `test_evaluate_donor_match_scoring`: Tests 100-point algorithm score calculation and explanation breakdown.
12. `test_contact_matched_donor_creates_notification`: Verifies notification generation upon donor outreach.
13. `test_donor_accepts_request_flow`: Tests donor acceptance decision and phone number release to requester.
14. `test_create_and_read_notification`: Tests in-app notification creation and mark-as-read mechanics.
15. `test_mark_all_read`: Tests bulk read status update.

---

## 10. Future Enhancements
1. **SMS & WhatsApp Gateway Integration:** Integrate Twilio or Gupshup for urgent SMS alerts when donors do not have active internet connections.
2. **GPS & Geolocation Mapping:** Interactive Leaflet / OpenStreetMap mapping displaying hospital locations and donor travel radii.
3. **Hospital EMR / EHR Integration:** HL7 / FHIR protocol connectors to interface directly with hospital laboratory information systems.
4. **Blood Bank Inventory Management:** Component separation tracking (Packed Red Cells, Fresh Frozen Plasma, Cryoprecipitate, and Platelets).
