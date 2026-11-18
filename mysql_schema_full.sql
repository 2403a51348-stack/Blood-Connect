-- ==============================================================================
-- BloodConnect MySQL Database Complete Schema DDL Script
-- ==============================================================================
-- Compatible with MySQL 8.0+ and MySQL Workbench
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS bloodconnect_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE bloodconnect_db;

-- 1. Accounts: User Profile (Role extension for standard auth_user)
CREATE TABLE IF NOT EXISTS accounts_userprofile (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'DONOR',
    phone VARCHAR(15) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Telangana',
    address TEXT NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX idx_userprofile_role (role),
    INDEX idx_userprofile_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Donors: Donor Profile
CREATE TABLE IF NOT EXISTS donors_donorprofile (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    blood_group VARCHAR(5) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Telangana',
    address TEXT NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    last_donation_date DATE NULL,
    total_donations INT UNSIGNED NOT NULL DEFAULT 0,
    availability_updated_at DATETIME(6) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX idx_donor_blood_group (blood_group),
    INDEX idx_donor_city (city),
    INDEX idx_donor_is_available (is_available)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Donors: Donation History
CREATE TABLE IF NOT EXISTS donors_donationhistory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    donor_id BIGINT NOT NULL,
    blood_request_id BIGINT NULL,
    donation_date DATE NOT NULL,
    units_donated INT UNSIGNED NOT NULL DEFAULT 1,
    hospital_name VARCHAR(200) NOT NULL,
    notes TEXT NOT NULL,
    verified_by_hospital BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME(6) NOT NULL,
    INDEX idx_donationhistory_donor (donor_id),
    INDEX idx_donationhistory_date (donation_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Requests: Requester Profile
CREATE TABLE IF NOT EXISTS requests_app_requesterprofile (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Telangana',
    address TEXT NOT NULL,
    organization_name VARCHAR(200) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX idx_requester_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Requests: Blood Request
CREATE TABLE IF NOT EXISTS requests_app_bloodrequest (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    request_id VARCHAR(30) NOT NULL UNIQUE,
    requester_id INT NOT NULL,
    patient_name VARCHAR(150) NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    units_required INT UNSIGNED NOT NULL DEFAULT 1,
    hospital_name VARCHAR(200) NOT NULL,
    hospital_address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Telangana',
    contact_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(15) NOT NULL,
    urgency VARCHAR(20) NOT NULL DEFAULT 'HIGH',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    additional_notes TEXT NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX idx_request_blood_group (blood_group),
    INDEX idx_request_city (city),
    INDEX idx_request_urgency (urgency),
    INDEX idx_request_status (status),
    INDEX idx_request_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Matching: Donor Match (Preliminary Algorithm Results)
CREATE TABLE IF NOT EXISTS matching_donormatch (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    blood_request_id BIGINT NOT NULL,
    donor_id BIGINT NOT NULL,
    match_score INT UNSIGNED NOT NULL DEFAULT 0,
    match_reasons TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'SUGGESTED',
    contacted_at DATETIME(6) NULL,
    responded_at DATETIME(6) NULL,
    created_at DATETIME(6) NOT NULL,
    UNIQUE KEY uq_request_donor (blood_request_id, donor_id),
    INDEX idx_match_score (match_score),
    INDEX idx_match_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Matching: Donation Response
CREATE TABLE IF NOT EXISTS matching_donationresponse (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    donor_match_id BIGINT NOT NULL,
    donor_id BIGINT NOT NULL,
    blood_request_id BIGINT NOT NULL,
    response VARCHAR(20) NOT NULL,
    remarks TEXT NOT NULL,
    responded_at DATETIME(6) NOT NULL,
    INDEX idx_response_decision (response)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Notifications: In-App User Notifications
CREATE TABLE IF NOT EXISTS notifications_notification (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    recipient_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(30) NOT NULL DEFAULT 'SYSTEM',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    related_url VARCHAR(255) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    INDEX idx_notification_recipient (recipient_id),
    INDEX idx_notification_is_read (is_read),
    INDEX idx_notification_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Dashboard: Administrative Activity & Security Log
CREATE TABLE IF NOT EXISTS dashboard_adminactivitylog (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    admin_user_id INT NULL,
    action_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    target_model VARCHAR(50) NOT NULL,
    target_id VARCHAR(50) NOT NULL,
    ip_address VARCHAR(39) NULL,
    timestamp DATETIME(6) NOT NULL,
    INDEX idx_adminlog_timestamp (timestamp),
    INDEX idx_adminlog_action (action_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'BloodConnect Database Schema successfully verified.' AS Confirmation;
