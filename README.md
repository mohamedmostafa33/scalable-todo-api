# Scalable Todo API

A production-ready, highly scalable backend API built with **Django REST Framework**, **MongoDB**, and **Kubernetes**. Deployed on **AWS EKS** with automatic scaling, high availability, and comprehensive monitoring capabilities.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Features](#project-features)
- [Repository Structure](#repository-structure)
- [API Endpoints](#api-endpoints)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Docker Build & Push](#docker-build--push)
- [Cluster Prerequisites Setup](#cluster-prerequisites-setup)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Monitoring & Scaling](#monitoring--scaling)
- [High Availability & Failover](#high-availability--failover)
- [Testing & Validation](#testing--validation)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)

---

## Overview

**Scalable Todo API** is a modern backend service that demonstrates enterprise-level DevOps practices, Kubernetes orchestration, and cloud-native architecture. The project implements a simple yet complete CRUD API for managing todos with built-in scalability, fault tolerance, and deployment automation.

**Deployment Steps (in order):**
1. Set up EKS cluster with Terraform
2. Install cluster-level prerequisites (EBS CSI, NGINX Ingress, Metrics Server)
3. Deploy application using kubectl manifests
4. Configure ingress and enable auto-scaling

**Key Highlights:**
- Auto-scaling pods based on CPU utilization (70% threshold)
- MongoDB Replica Set with 3 nodes for data redundancy
- Health checks with readiness and liveness probes
- Load-balanced via NGINX Ingress Controller
- Persistent data storage with Kubernetes PVCs

---

## Architecture

```
                     AWS EKS Cluster
                              
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL TRAFFIC                        │
│                     (Client Requests)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                NGINX Ingress Controller                     │
│              (Route /api → Service:8000)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
    ┌─────────────┐            ┌──────────────────┐
    │   Load      │            │  Health Check    │
    │   Balance   │            │  /api/health/    │
    └─────────────┘            └──────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│         API SERVICE LAYER (ClusterIP: Port 8000)            │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
    ┌──────────────┐              ┌─────────────────┐
    │ Deployment   │              │ Horizontal Pod  │
    │ (5 Replicas) │◄─────────────┤ Autoscaler      │
    │              │              │ (1-5 replicas,  │
    │ Django + DRF │              │  70% CPU)       │
    │ Pods         │              └─────────────────┘
    └──────────────┘
          │
          ├─ Pod Replica 1
          ├─ Pod Replica 2
          ├─ Pod Replica 3
          └─ Pod Replica N
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│       DATABASE SERVICE LAYER (ClusterIP: Port 27017)        │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
    ┌──────────────┐              ┌────────────────┐
    │ StatefulSet  │              │ MongoDB        │
    │ (3 Replicas) │              │ Replica Set    │
    │              │              │ rs0            │
    │ MongoDB 8.0  │              └────────────────┘
    └──────────────┘
          │
          ├─ todo-statefulset-0 [Primary]   ◄─ PVC: 1Gi
          ├─ todo-statefulset-1 [Secondary] ◄─ PVC: 1Gi
          └─ todo-statefulset-2 [Secondary] ◄─ PVC: 1Gi
          │
          ▼
    ┌────────────────────────┐
    │ Persistent Volumes     │
    │ (Durable Storage)      │
    │ ReplicaSet rs0         │
    │ Auto-failover enabled  │
    └────────────────────────┘
```

**Request Flow & System Behavior:**

- **External Traffic**: Client requests enter through the NGINX Ingress Controller, which routes `/api/*` traffic to the API ClusterIP Service on port 8000.
  
- **API Layer Scaling**: The Deployment manages 5 API pod replicas (configurable). The Horizontal Pod Autoscaler continuously monitors CPU usage and automatically scales between 1-5 replicas to maintain the 70% CPU utilization target.

- **Database Connectivity**: API pods communicate with MongoDB through the MongoDB ClusterIP Service on port 27017. The StatefulSet ensures stable DNS naming for replica set initialization and discovery.

- **MongoDB High Availability**: The StatefulSet maintains 3 MongoDB replicas (Primary + 2 Secondaries) with automatic failover enabled. If a replica fails, Kubernetes recreates it, and the replica set automatically re-syncs data.

- **Data Persistence**: Each MongoDB replica has a dedicated 1Gi PersistentVolumeClaim (PVC), ensuring data survives pod restarts and node failures. Persistent Volumes are mounted at `/data/db` in each pod.

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **API Framework** | Django REST Framework | 3.16.1 |
| **Backend Language** | Python | 3.12 |
| **Database** | MongoDB | 8.0 |
| **ODM** | MongoEngine | 0.29.3 |
| **Container** | Docker | Latest |
| **Orchestration** | Kubernetes | 1.30 |
| **Cloud Provider** | AWS EKS | Latest |
| **Ingress Controller** | NGINX | Latest |
| **Package Manager** | pip | Latest |

---

## Project Features

- **CRUD Todo API**: Full Create, Read, Update, Delete functionality
- **RESTful Design**: Follows REST best practices for clean API design
- **MongoDB Replica Set**: 3-node replica set for high availability and data redundancy
- **Horizontal Pod Autoscaling**: Automatic scaling from 1 to 5 pods based on CPU load
- **Health Checks**: Readiness and liveness probes for reliable pod management
- **Persistent Storage**: Kubernetes PersistentVolumeClaims for MongoDB data retention
- **NGINX Ingress**: External traffic routing with a single entry point
- **ClusterIP Services**: Internal service discovery and load balancing
- **Configurable via ConfigMap**: Environment variables managed through Kubernetes ConfigMaps
- **Production-Grade Deployment**: Resource requests/limits, proper logging, and error handling

---

## Repository Structure

```
scalable-todo-api/
├── Dockerfile              # Multi-stage Docker build for the API
├── README.md              # This file
├── .dockerignore          # Docker build exclusions
│
├── src/                   # Django application source code
│   ├── manage.py          # Django management script
│   ├── requirements.txt   # Python dependencies
│   ├── api/               # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py    # Django configuration, MongoDB connection
│   │   ├── urls.py        # URL routing
│   │   ├── asgi.py        # ASGI configuration
│   │   └── wsgi.py        # WSGI configuration
│   ├── todo/              # Todo app (CRUD logic)
│   │   ├── __init__.py
│   │   ├── models.py      # Todo MongoEngine model
│   │   ├── serializers.py # DRF serializers for Todo
│   │   ├── views.py       # API viewsets
│   │   ├── urls.py        # Todo app routes
│   │   └── migrations/    # Database migrations
│   └── venv/              # Virtual environment (git-ignored)
│
├── k8s/                   # Kubernetes manifests
│   ├── api/               # API deployment manifests
│   │   ├── configmap.yaml      # Environment variables
│   │   ├── deployment.yaml     # API Deployment (5 replicas)
│   │   ├── service.yaml        # ClusterIP Service
│   │   ├── hpa.yaml           # Horizontal Pod Autoscaler
│   │   └── ingress.yaml       # NGINX Ingress
│   └── db/                # MongoDB deployment manifests
│       ├── service.yaml        # Headless Service
│       └── statefulset.yaml    # MongoDB StatefulSet (3 replicas)
│
└── .gitignore            # Git exclusions
```

---

## API Endpoints

All endpoints are prefixed with `/api/` and respond with JSON.

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| **GET** | `/todos/` | List all todos | None | Array of todos |
| **POST** | `/todos/` | Create new todo | `{"title": "...", "description": "...", "completed": false}` | Created todo with `id` |
| **GET** | `/todos/{id}/` | Retrieve specific todo | None | Single todo object |
| **PUT** | `/todos/{id}/` | Replace entire todo | `{"title": "...", "description": "...", "completed": ...}` | Updated todo |
| **PATCH** | `/todos/{id}/` | Partial update todo | `{"completed": true}` | Updated todo |
| **DELETE** | `/todos/{id}/` | Delete todo | None | HTTP 204 No Content |
| **GET** | `/health/` | Health check endpoint | None | `{"status": "healthy"}` |

### Todo Model Schema

```json
{
  "id": "507f1f77bcf86cd799439011",  // MongoDB ObjectId (string)
  "title": "Complete project",        // Required, max 255 chars
  "description": "Finish deployment", // Optional
  "completed": false                  // Boolean, default: false
}
```

### Example API Calls

```bash
# Create a new todo
curl -X POST http://localhost:8000/api/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread", "completed": false}'

# List all todos
curl http://localhost:8000/api/todos/

# Get specific todo
curl http://localhost:8000/api/todos/507f1f77bcf86cd799439011/

# Update todo (PATCH)
curl -X PATCH http://localhost:8000/api/todos/507f1f77bcf86cd799439011/ \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete todo
curl -X DELETE http://localhost:8000/api/todos/507f1f77bcf86cd799439011/

# Health check
curl http://localhost:8000/api/health/
```

---

## Prerequisites

- **Docker**: For containerization
- **Kubernetes Cluster**: EKS, GKE, or local (minikube/kind)
- **kubectl**: Kubernetes command-line tool (v1.30+)
- **Helm**: For installing Kubernetes packages (v3.0+)
- **AWS CLI**: If deploying to AWS
- **Python 3.12+**: For local development
- **Git**: For version control

**Note**: After creating your EKS cluster, you must install cluster-level prerequisites before deploying the application. See the "Cluster Prerequisites Setup" section below.

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/scalable-todo-api.git
cd scalable-todo-api
```

### 2. Create Python Virtual Environment

```bash
cd src
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp api/.env.example api/.env
```

Edit `src/api/.env`:

```env
MONGO_URI=mongodb://localhost:27017/todo_db
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run MongoDB Locally

```bash
# Using Docker
docker run -d \
  --name mongo \
  -p 27017:27017 \
  mongo:8.0

# Or using MongoDB Community Edition directly
mongod --dbpath /data/db
```

### 6. Start Django Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Access the API at `http://localhost:8000/api/todos/`

---

## Docker Build & Push

### Prerequisites

- Docker installed and running
- Docker Hub account (or any container registry)

### Build Docker Image

```bash
# Build image
docker build -t your-dockerhub-username/todo_api:v1 .

# Verify build
docker images | grep todo_api
```

### Test Image Locally

```bash
# Run container
docker run -d \
  --name todo-api-test \
  -p 8000:8000 \
  -e MONGO_URI=mongodb://mongo:27017/todo_db \
  your-dockerhub-username/todo_api:v1

# Test endpoint
curl http://localhost:8000/api/health/

# Stop container
docker stop todo-api-test
```

### Push to Docker Hub

```bash
# Login to Docker Hub
docker login -u your-username

# Push image
docker push your-dockerhub-username/todo_api:v1

# Verify on Docker Hub
# Visit: https://hub.docker.com/r/your-dockerhub-username/todo_api
```

---

## Cluster Prerequisites Setup

Before deploying the application, install these three components:

### Step 0.1: EBS CSI Driver

```bash
# Add EKS add-on
ROLE_ARN=$(aws iam get-role --role-name AmazonEKS_EBS_CSI_DriverRole \
  --query 'Role.Arn' --output text)

aws eks create-addon \
  --cluster-name todo-eks \
  --addon-name aws-ebs-csi-driver \
  --service-account-role-arn "$ROLE_ARN" \
  --region us-east-1

# Verify
kubectl get daemonset -n kube-system ebs-csi-node
```

### Step 0.2: NGINX Ingress Controller

```bash
# Deploy NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/aws/deploy.yaml

# Wait for LoadBalancer
kubectl get svc -n ingress-nginx ingress-nginx-controller -w
```

### Step 0.3: Metrics Server

```bash
# Install Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify
kubectl get deployment -n kube-system metrics-server
```

---

## Kubernetes Deployment

**Prerequisites:**
- Complete "Cluster Prerequisites Setup" first (EBS CSI, NGINX Ingress, Metrics Server)
- EKS cluster running and `kubectl` configured
- Docker image built and pushed to registry

### Step 1: Create Namespace

```bash
kubectl create namespace todo-app
```

### Step 2: Deploy MongoDB Replica Set

```bash
# Deploy MongoDB
kubectl apply -f k8s/db/service.yaml -n todo-app
kubectl apply -f k8s/db/statefulset.yaml -n todo-app

# Wait for StatefulSet to be ready
kubectl rollout status statefulset/todo-statefulset -n todo-app
```

### Step 3: Initialize MongoDB Replica Set

```bash
# Get MongoDB pod name
MONGO_POD=$(kubectl get pods -n todo-app -l app=todo-db -o jsonpath='{.items[0].metadata.name}')

# Initialize replica set (run inside the pod)
kubectl exec -it $MONGO_POD -n todo-app -- mongosh --eval "
rs.initiate({
  _id: 'rs0',
  members: [
    { _id: 0, host: 'todo-statefulset-0.todo-db-service:27017' },
    { _id: 1, host: 'todo-statefulset-1.todo-db-service:27017' },
    { _id: 2, host: 'todo-statefulset-2.todo-db-service:27017' }
  ]
})
"
```

### Step 4: Deploy API ConfigMap and Secrets

```bash
kubectl apply -f k8s/api/configmap.yaml -n todo-app
```

### Step 5: Deploy API

```bash
# Create API Service
kubectl apply -f k8s/api/service.yaml -n todo-app

# Create API Deployment
kubectl apply -f k8s/api/deployment.yaml -n todo-app

# Wait for deployment
kubectl rollout status deployment/todo-api-deployment -n todo-app
```

### Step 6: Deploy HPA

```bash
kubectl apply -f k8s/api/hpa.yaml -n todo-app
```

### Step 7: Deploy Ingress

```bash
kubectl apply -f k8s/api/ingress.yaml -n todo-app
```

### Step 8: Verify Deployment

```bash
# Check all resources
kubectl get all -n todo-app

# Check pods
kubectl get pods -n todo-app

# Check deployments
kubectl get deployments -n todo-app

# Check services
kubectl get svc -n todo-app

# Check HPA status
kubectl get hpa -n todo-app

# Check logs
kubectl logs -f deployment/todo-api-deployment -n todo-app

# Check ingress
kubectl get ingress -n todo-app
```

---

## Monitoring & Scaling

### Horizontal Pod Autoscaler (HPA)

The HPA automatically scales your API pods based on CPU usage:

**Configuration:**
- **Minimum Replicas**: 1
- **Maximum Replicas**: 5
- **CPU Target**: 70% average utilization

### Check HPA Status

```bash
# Watch HPA in real-time
kubectl get hpa -n todo-app -w

# Detailed HPA info
kubectl describe hpa todo-api-hpa -n todo-app
```

### Load Testing (Generate Traffic to Trigger Scaling)

```bash
# Method 1: Using Apache Bench
ab -n 10000 -c 100 http://<ingress-ip>/api/health/

# Method 2: Using hey (modern alternative)
hey -n 10000 -c 100 http://<ingress-ip>/api/health/

# Method 3: Using kubectl run + busybox
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://todo-api-service:8000/api/health/; done"
```

### Monitor Pod Scaling in Real-Time

```bash
# Terminal 1: Watch pods
kubectl get pods -n todo-app -w

# Terminal 2: Generate load (from above)
# Terminal 3: Monitor HPA
kubectl get hpa -n todo-app -w
```

### View Resource Metrics

```bash
# Install metrics-server if not already installed
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Check metrics
kubectl top nodes
kubectl top pods -n todo-app
```

---

## High Availability & Failover

### MongoDB Replica Set Architecture

**Why Replica Sets?**
- **Data Redundancy**: Data is replicated across 3 nodes
- **Automatic Failover**: If primary fails, a secondary is elected
- **Read Scaling**: Read operations can be distributed across replicas
- **Consistency**: Strong consistency model with configurable read preferences

**Replica Set Topology:**
```
Primary (todo-statefulset-0)
   ↓
Secondary (todo-statefulset-1)
Secondary (todo-statefulset-2)
```

### Test Pod Deletion (High Availability)

#### Test 1: Delete API Pod

```bash
# Get pod name
API_POD=$(kubectl get pods -n todo-app -l app=todo-api -o jsonpath='{.items[0].metadata.name}')

# Delete the pod
kubectl delete pod $API_POD -n todo-app

# Watch immediate re-creation
kubectl get pods -n todo-app -w
```

**Expected Result**: Kubernetes immediately spins up a replacement pod.

#### Test 2: Delete MongoDB Pod

```bash
# Get MongoDB pod
MONGO_POD=$(kubectl get pods -n todo-app -l app=todo-db -o jsonpath='{.items[0].metadata.name}')

# Delete the pod
kubectl delete pod $MONGO_POD -n todo-app

# Verify replica set recovers
kubectl exec -it todo-statefulset-0 -n todo-app -- mongosh --eval "rs.status()"
```

**Expected Result**: 
- StatefulSet recreates the pod
- Replica set re-syncs data automatically
- API continues functioning with reduced capacity (briefly)

#### Test 3: Verify Data Persistence

```bash
# Create a todo
curl -X POST http://<ingress-ip>/api/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Test persistence", "completed": false}'

# Delete all MongoDB pods
kubectl delete pods -n todo-app -l app=todo-db

# Wait for recreation
sleep 10

# Verify data still exists
curl http://<ingress-ip>/api/todos/
```

**Expected Result**: Todo data persists after pod deletion.

---

## Testing & Validation

### Health Check

```bash
# Simple health check
curl http://<ingress-ip>/api/health/

# Should return:
# {"status": "healthy"}
```

### CRUD Operations Test

```bash
# 1. CREATE
TODO_ID=$(curl -s -X POST http://<ingress-ip>/api/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Todo", "description": "Testing CRUD", "completed": false}' \
  | jq -r '.id')

echo "Created todo with ID: $TODO_ID"

# 2. READ
curl http://<ingress-ip>/api/todos/$TODO_ID/ | jq .

# 3. UPDATE
curl -X PATCH http://<ingress-ip>/api/todos/$TODO_ID/ \
  -H "Content-Type: application/json" \
  -d '{"completed": true}' | jq .

# 4. DELETE
curl -X DELETE http://<ingress-ip>/api/todos/$TODO_ID/
```

### Performance Testing

```bash
# Measure response time
time curl http://<ingress-ip>/api/todos/ > /dev/null

# Load test with concurrency
ab -n 1000 -c 50 http://<ingress-ip>/api/health/

# Expected result: < 500ms response time under normal load
```

### Kubernetes Probe Verification

```bash
# Check readiness probe logs
kubectl describe pod <pod-name> -n todo-app | grep -A 5 "Readiness"

# Check liveness probe logs
kubectl describe pod <pod-name> -n todo-app | grep -A 5 "Liveness"

# View probe events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

---

## Conclusion

**Scalable Todo API** demonstrates production-grade DevOps practices by combining:
- Modern backend framework (Django REST Framework)
- Containerized application (Docker)
- Orchestrated infrastructure (Kubernetes)
- Cloud-native design (AWS EKS)
- High availability and automatic scaling

This project serves as a reference architecture for building scalable, resilient applications on Kubernetes and AWS.