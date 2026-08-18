-- Sales Intelligence Hub — Consolidated Schema
-- This mirrors exactly what branches.py / customer_sales.py / users.py /
-- payment_split.py create at runtime. It exists as a single reviewable
-- deliverable — you don't need to run this file separately; running the
-- four setup scripts in order (see README.md) builds this same schema.

CREATE DATABASE IF NOT EXISTS Sales_Management;
USE Sales_Management;

-- 1. branch
CREATE TABLE branch (
    branch_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_name VARCHAR(100) NOT NULL,
    branch_admin_name VARCHAR(100) NOT NULL
);

-- 2. customer_sales
CREATE TABLE customer_sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_id INT,
    date DATE DEFAULT (CURRENT_DATE),
    name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(15),
    product_name VARCHAR(30),
    gross_sales DECIMAL(12,2) NOT NULL,
    received_amount DECIMAL(12,2) DEFAULT 0,
    pending_amount DECIMAL(12,2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status ENUM('Open','Close') DEFAULT 'Open',
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

DELIMITER //
CREATE TRIGGER before_sale_insert
BEFORE INSERT ON customer_sales
FOR EACH ROW
BEGIN
    IF NEW.gross_sales - NEW.received_amount <= 0 THEN
        SET NEW.status = 'Close';
    ELSE
        SET NEW.status = 'Open';
    END IF;
END//

CREATE TRIGGER before_sale_update
BEFORE UPDATE ON customer_sales
FOR EACH ROW
BEGIN
    IF NEW.gross_sales - NEW.received_amount <= 0 THEN
        SET NEW.status = 'Close';
    ELSE
        SET NEW.status = 'Open';
    END IF;
END//
DELIMITER ;

-- 3. users
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,   -- stores a SHA-256 hash, never plaintext
    branch_id INT,
    role ENUM('Super Admin', 'Admin'),
    email VARCHAR(255) NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

DELIMITER //
CREATE TRIGGER before_user_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.role = 'Super Admin'
    AND EXISTS (SELECT 1 FROM users WHERE role = 'Super Admin')
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only one Super Admin is allowed';
    END IF;
END//

CREATE TRIGGER before_user_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    IF NEW.role = 'Super Admin'
    AND OLD.role <> 'Super Admin'
    AND EXISTS (
        SELECT 1 FROM users
        WHERE role = 'Super Admin' AND user_id <> OLD.user_id
    )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only one Super Admin is allowed';
    END IF;
END//
DELIMITER ;

-- 4. payment_split
CREATE TABLE payment_split (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT,
    payment_date DATE,
    amount_paid DECIMAL(12,2),
    payment_method VARCHAR(50),
    FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id)
);

DELIMITER //
CREATE TRIGGER after_split_insert
AFTER INSERT ON payment_split
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = (
        SELECT COALESCE(SUM(amount_paid), 0)
        FROM payment_split
        WHERE sale_id = NEW.sale_id
    )
    WHERE sale_id = NEW.sale_id;
END//
DELIMITER ;
