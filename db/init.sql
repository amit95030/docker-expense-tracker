CREATE DATABASE IF NOT EXISTS expensesdb;

USE expensesdb;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(100),
    amount DECIMAL(10,2),
    note TEXT,
    date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
