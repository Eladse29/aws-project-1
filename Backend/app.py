from flask import Flask, request
import psycopg2
import requests
import boto3
import re

app = Flask(__name__)

s3 = boto3.client("s3", region_name="us-east-1")
sns = boto3.client("sns", region_name="us-east-1")

BUCKET_NAME = "amzn-s3-bucket-demo-1"
TOPIC_ARN = "arn:aws:sns:us-east-1:904053120094:first_SNS_topic"

VALID_OS = ["ubuntu-22.04-lts", "ubuntu-24.04-lts", "debian-12"]
VALID_CPU = [1, 2, 4, 8]
VALID_RAM = [2, 4, 8, 16]

VALID_CPU_RAM = {
    1: [2, 4],
    2: [4, 8],
    4: [8, 16],
    8: [16]
}

def get_connection():
    return psycopg2.connect(
        host="devops-project-db.ckhueoagg405.us-east-1.rds.amazonaws.com",
        database="postgres",
        user="postgres",
        password="Aa!123456",
        port="5432"
    )

@app.route("/")
def home():
    return "Backend running with DB"

@app.route("/provision", methods=["POST"])
def provision():
    data = request.json or {}

    name = data.get("name", "").strip()
    os_name = data.get("os")
    cpu = data.get("cpu")
    ram_gb = data.get("ram_gb")

    if not name:
        return {"status": "error", "message": "VM name is required"}, 400

    if len(name) < 2:
        return {"status": "error", "message": "VM name must contain at least 2 characters"}, 400

    if not re.match(r"^[A-Za-z0-9_-]+$", name):
        return {
            "status": "error",
            "message": "VM name must contain only English letters, numbers, hyphen or underscore"
        }, 400

    if os_name not in VALID_OS:
        return {"status": "error", "message": "Invalid operating system"}, 400

    if cpu not in VALID_CPU:
        return {"status": "error", "message": "Invalid CPU value"}, 400

    if ram_gb not in VALID_RAM:
        return {"status": "error", "message": "Invalid RAM value"}, 400

    if ram_gb not in VALID_CPU_RAM[cpu]:
        return {
            "status": "error",
            "message": f"Invalid CPU/RAM combination. {cpu} CPU supports only {VALID_CPU_RAM[cpu]} GB RAM"
        }, 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO items (name, os, cpu, ram_gb) VALUES (%s, %s, %s, %s)",
        (name, os_name, cpu, ram_gb)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "added",
        "machine": {
            "name": name,
            "os": os_name,
            "cpu": cpu,
            "ram_gb": ram_gb
        }
    }

@app.route("/machines", methods=["GET"])
def machines():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, os, cpu, ram_gb FROM items ORDER BY id")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "name": row[1],
            "os": row[2],
            "cpu": row[3],
            "ram_gb": row[4]
        })

    return {"items": items}

@app.route("/worker-health", methods=["GET"])
def worker_health():
    response = requests.get("http://10.0.0.195:5001/health")
    return response.json()

@app.route("/upload", methods=["POST"])
def upload_file():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, os, cpu, ram_gb
        FROM items
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {
            "status": "error",
            "message": "No machines found in database"
        }, 400

    vm_id = row[0]
    vm_name = row[1]
    vm_os = row[2]
    vm_cpu = row[3]
    vm_ram = row[4]

    content = f"""
VM Provisioning Report

Machine ID: {vm_id}
Name: {vm_name}
Operating System: {vm_os}
CPU: {vm_cpu}
RAM: {vm_ram}GB
"""

    filename = f"vm-report-{vm_id}.txt"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=filename,
        Body=content
    )

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="VM Provisioning Report Uploaded",
        Message=f"""
A VM provisioning report was uploaded to S3.

Machine Name: {vm_name}
Operating System: {vm_os}
CPU: {vm_cpu}
RAM: {vm_ram}GB

S3 File: {filename}
"""
    )

    return {
        "status": "uploaded",
        "bucket": BUCKET_NAME,
        "file": filename,
        "sns": "notification sent"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)