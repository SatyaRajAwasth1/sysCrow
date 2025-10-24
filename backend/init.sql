-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS processed_logs;

-- Switch to the processed_logs database
USE processed_logs;

-- Create table for storing log entries
CREATE TABLE IF NOT EXISTS log_entries (
  id INT NOT NULL AUTO_INCREMENT,
  timestamp DATETIME NOT NULL,
  thread VARCHAR(255) DEFAULT NULL,
  level VARCHAR(50) DEFAULT NULL,
  correlation_id VARCHAR(255) DEFAULT NULL,
  logger_name VARCHAR(255) DEFAULT NULL,
  template_id VARCHAR(255) DEFAULT NULL,
  properties JSON DEFAULT NULL,
  PRIMARY KEY (id),
  KEY template_id (template_id),
  CONSTRAINT log_details_ibfk_1 FOREIGN KEY (template_id) REFERENCES log_templates (template_id)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create table for storing log templates
CREATE TABLE IF NOT EXISTS log_templates (
  id INT NOT NULL AUTO_INCREMENT,
  template_id VARCHAR(255) NOT NULL,
  template_text TEXT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY template_id (template_id)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Create table for storing unsupervised segmented sequences
CREATE TABLE IF NOT EXISTS unsupervised_segmented_sequences (
  line_sequence VARCHAR(1000) DEFAULT NULL,
  event_sequence VARCHAR(1000) DEFAULT NULL,
  correlation_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  timestamp DATETIME DEFAULT NULL,
  batch VARCHAR(255) DEFAULT NULL,
  id BIGINT NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Create table for storing suspicious log sequences
CREATE TABLE IF NOT EXISTS suspicious_log_sequences (
  batch VARCHAR(100) DEFAULT NULL,
  line_sequence VARCHAR(1000) DEFAULT NULL,
  event_sequence VARCHAR(1000) DEFAULT NULL,
  correlation_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  timestamp DATETIME DEFAULT NULL,
  confidence FLOAT DEFAULT NULL,
  id BIGINT NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;