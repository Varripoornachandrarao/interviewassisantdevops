# AI Interview Assistant - DevOps Implementation

An automated CI/CD pipeline for a containerized AI-powered Interview Assistant, deployed on AWS using Docker, Kubernetes, and Jenkins.

## 🚀 Architecture Overview
- **Frontend**: Nginx serving a Tailwind CSS + Vanilla JS UI.
- **Backend**: Flask API using LangChain (Gemini), Murf AI (TTS), and AssemblyAI (STT).
- **Database/State**: Redis for session persistence across multiple replicas.
- **CI/CD**: Jenkins pipeline for automated testing, building, and K8s deployment.
- **Infrastructure**: Terraform for provisioning AWS VPC and EC2 instances.
- **Orchestration**: Kubernetes with HPA (Horizontal Pod Autoscaling).
- **Monitoring**: Prometheus for performance tracking.

## 📁 Project Structure
```text
.
├── backend/            # Flask application & Dockerfile
├── frontend/           # Static UI & Nginx config
├── k8s/                # Kubernetes manifests (Deployment, HPA, Redis)
├── terraform/          # Infrastructure as Code (AWS VPC/EC2)
├── prometheus/         # Monitoring configuration
├── Jenkinsfile         # CI/CD Pipeline definition
├── docker-compose.yml  # Local development orchestration
└── Makefile            # Task automation (build, test, up)
```

## 🛠️ Getting Started

### 1. External Requirements
To run this project, you need API keys for:
- Google Gemini (GenAI)
- Murf AI (Text-to-Speech)
- AssemblyAI (Speech-to-Text)

Add these to your `backend/.env` file.

### 2. Local Development
Use the provided `Makefile` to run the stack locally:
```bash
make build   # Build Docker images
make test    # Run backend unit tests
make up      # Start the entire stack (App + Redis + Prometheus)
```
The frontend will be available at `http://localhost:8080`.

### 3. Infrastructure (AWS)
Provision the AWS infrastructure using Terraform:
```bash
cd terraform
terraform init
terraform apply
```

### 4. Kubernetes Deployment
The Jenkins pipeline automatically handles deployments. To do it manually:
```bash
kubectl apply -f k8s/
```

## 📈 Monitoring
Access the Prometheus dashboard at `http://localhost:9090` to monitor the Flask backend and system health.

## 🛡️ DevOps Features
- **Scalability**: HPA scales the backend pods based on CPU utilization.
- **High Availability**: Redis shared state allows seamless load balancing.
- **Security**: Non-root Docker users and K8s secrets.
- **Persistence**: Session data persists even if pods restart.
