# AI Interview Assistant - DevOps Implementation

An automated CI/CD pipeline for a containerized AI-powered Interview Assistant, deployed on an AWS EC2 instance using Docker and GitHub Actions.

## 🚀 Architecture Overview
- **Frontend**: Nginx serving a Tailwind CSS + Vanilla JS UI.
- **Backend**: Flask API using LangChain (Gemini), Murf AI (TTS), and AssemblyAI (STT).
- **Database/State**: Redis for session persistence.
- **CI/CD**: GitHub Actions pipeline for automated building, pushing to Docker Hub, and EC2 deployment.
- **Orchestration**: Docker Compose.
- **Monitoring**: Prometheus for performance tracking.

## 📁 Project Structure
```text
.
├── .github/workflows/  # GitHub Actions pipeline (deploy.yml)
├── backend/            # Flask application & Dockerfile
├── frontend/           # Static UI & Nginx config
├── prometheus/         # Monitoring configuration
├── docker-compose.yml  # Local development orchestration
├── docker-compose.prod.yml # Production orchestration for EC2
└── Makefile            # Task automation (build, test, up)
```

## 🛠️ Getting Started

### 1. External Requirements
To run this project, you need API keys for:
- Google Gemini (GenAI)
- Murf AI (Text-to-Speech)
- AssemblyAI (Speech-to-Text)

Create `backend/.env` from `backend/.env.example` and add your keys.

### 2. Local Development
Use the provided `Makefile` to run the stack locally:
```bash
make build   # Build Docker images
make test    # Run backend unit tests
make up      # Start the entire stack (App + Redis + Prometheus)
```
The frontend will be available at `http://localhost:8080`.

### 3. Production Deployment (GitHub Actions)
The infrastructure is automatically deployed using GitHub actions to an AWS EC2 instance. 

**Required GitHub Pipeline Secrets:**
- `DOCKERHUB_USERNAME`: Your Docker Hub username.
- `DOCKERHUB_TOKEN`: Your Docker Hub access token.
- `EC2_HOST`: The Public IP of your EC2 instance.
- `EC2_SSH_KEY`: The private `.pem` key to SSH into the EC2 instance.

**Important Note for EC2:**
After the first deployment, you must SSH into the EC2 instance and manually add your `.env` keys to:
`~/interview-app/backend/.env`

## 📈 Monitoring
Access the Prometheus dashboard at `http://YOUR_EC2_IP:9090` to monitor the Flask backend and system health.

## 🛡️ DevOps Features
- **CI/CD Automation**: Fully automated deployment upon push to the `main` branch.
- **High Availability**: Redis shared state allows the backend to be stateless.
- **Security**: Non-root Docker users for enhanced container isolation.
