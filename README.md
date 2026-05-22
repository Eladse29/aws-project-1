# DevOps AWS Project – Multi-Service Cloud Application

## Project Overview

This project demonstrates a simple multi-service cloud application running on AWS infrastructure.

The application simulates a lightweight VM provisioning platform where users can create virtual machine records through a web interface.
The system stores VM data in a PostgreSQL RDS database, generates provisioning reports, uploads them to AWS S3, and sends notifications through AWS SNS.

The architecture is based on three separate services running on independent EC2 instances.

---

# Architecture

The application consists of:

1. Frontend Service (nginx)
2. Backend API Service (Flask)
3. Worker Service (Flask)

Additional AWS services:

* Amazon RDS PostgreSQL
* Amazon S3
* Amazon SNS

---

# Services Description

## 1. Frontend Service

### Technologies

* nginx
* HTML
* JavaScript

### Responsibilities

* Provides the user interface
* Allows users to create VM records
* Displays provisioned machines
* Sends requests to backend API
* Performs reverse proxying to backend service

### EC2 Role

Public-facing instance exposed through HTTP.

---

## 2. Backend Service

### Technologies

* Python Flask
* boto3
* psycopg2

### Responsibilities

* Handles API requests
* Performs validation
* Stores VM data in RDS
* Retrieves VM data from RDS
* Communicates with Worker service
* Uploads reports to S3
* Sends SNS notifications

### API Endpoints

| Endpoint         | Description                    |
| ---------------- | ------------------------------ |
| `/provision`     | Create VM                      |
| `/machines`      | List VMs                       |
| `/worker-health` | Check worker health            |
| `/upload`        | Upload report to S3 + send SNS |

---

## 3. Worker Service

### Technologies

* Python Flask

### Responsibilities

* Internal service used for health checks
* Demonstrates inter-service communication

### Endpoint

| Endpoint  | Description           |
| --------- | --------------------- |
| `/health` | Returns worker status |

---

# AWS Services Usage

## Amazon RDS

### Engine

PostgreSQL

### Purpose

Stores VM provisioning data.

### Table Structure

Table name: `items`

Columns:

* id
* name
* os
* cpu
* ram_gb

### Database Operations

* INSERT operation during VM creation
* SELECT operation for VM listing

---

## Amazon S3

### Bucket

`amzn-s3-bucket-demo-1`

### Purpose

Stores VM provisioning report files.

### Example Uploaded File

`vm-report-3.txt`

### File Content Example

```text
VM Provisioning Report

Machine ID: 3
Name: web-server-01
Operating System: ubuntu-22.04-lts
CPU: 2
RAM: 4GB
```

---

## Amazon SNS

### Purpose

Sends email notifications after report upload.

### Event Trigger

Uploading a provisioning report to S3.

### SNS Flow

1. User creates VM
2. Backend generates report
3. Report uploaded to S3
4. SNS notification email sent

---

# Networking and Communication

## Service Communication

```text
User Browser
     ↓
Frontend EC2 (nginx)
     ↓
Backend EC2 (Flask API)
     ↓
RDS PostgreSQL

Backend EC2
     ↓
Worker EC2

Backend EC2
     ↓
S3 + SNS
```

---

# Security

## Security Groups

### Frontend

Allowed:

* HTTP (80)
* SSH (22)

### Backend

Allowed:

* Port 5000 from Frontend EC2 only
* SSH (22)

### Worker

Allowed:

* Port 5001 from Backend EC2 only
* SSH (22)

### RDS

Allowed:

* PostgreSQL 5432 from Backend EC2 only

---

# IAM Permissions

The backend EC2 instance uses an IAM Role with permissions for:

* S3 object upload
* SNS publish

No static AWS credentials were stored in code.

---

# Validation Logic

The application validates:

* VM name format
* Allowed operating systems
* Valid CPU values
* Valid RAM values
* Valid CPU/RAM combinations

Examples:

* 1 CPU supports only 2GB or 4GB RAM
* 8 CPU supports only 16GB RAM

---

# Application Features

## Create VM

Creates a VM record and stores it in RDS.

## View Machines

Displays all provisioned machines from database.

## Worker Health Check

Checks internal communication with worker service.

## Upload Report

Creates provisioning report and uploads it to S3.

## SNS Notification

Sends email notification after upload.

---

# Installation and Setup

## Frontend

* Install nginx
* Configure reverse proxy
* Deploy `index.html`

## Backend

Install dependencies:

```bash
pip3 install flask psycopg2-binary boto3 requests
```

Run service:

```bash
python3 app.py
```

## Worker

Install Flask:

```bash
pip3 install flask
```

Run service:

```bash
python3 worker.py
```

---

# Systemd Services

The backend and worker services are configured as systemd services to start automatically after reboot.

Services:

* backend.service
* worker.service

---

# Screenshots Included

The submission includes screenshots of:

* EC2 instances
* RDS database
* S3 bucket
* SNS topic and subscription
* Application UI
* SQL query results
* SNS email notifications
* Upload flow

---

# Project Goals Achieved

* Multi-service architecture
* AWS cloud integration
* Database integration
* Object storage integration
* Notification system
* Internal networking
* Reverse proxy configuration
* Service health checks
* IAM role usage
* Security group configuration

---

# Future Improvements

Possible future improvements:

* HTTPS support
* Terraform automation
* Ansible deployment
* CloudWatch logging
* Authentication system
* Dynamic inventory
