#!/bin/bash
# ============================================================
# DevOps Server Setup Script
# Installs: Docker, Jenkins, kubectl, Helm
# Run on: Ubuntu 22.04 EC2
# Usage: chmod +x setup.sh && sudo ./setup.sh
# ============================================================

set -e
echo "========================================"
echo "  DevOps Server Setup Starting..."
echo "========================================"

# Update system
echo "[1/6] Updating system packages..."
apt-get update -y && apt-get upgrade -y

# Install Java (required for Jenkins)
echo "[2/6] Installing Java..."
apt-get install -y openjdk-17-jdk

# Install Docker
echo "[3/6] Installing Docker..."
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu
usermod -aG docker jenkins 2>/dev/null || true

# Install Jenkins
echo "[4/6] Installing Jenkins..."
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | tee /etc/apt/sources.list.d/jenkins.list > /dev/null
apt-get update -y
apt-get install -y jenkins
systemctl enable jenkins
systemctl start jenkins
usermod -aG docker jenkins

# Install kubectl
echo "[5/6] Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# Install Helm
echo "[6/6] Installing Helm..."
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo ""
echo "========================================"
echo "  ✅ Setup Complete!"
echo "========================================"
echo ""
echo "  Jenkins URL: http://$(curl -s ifconfig.me):8080"
echo ""
echo "  Jenkins initial admin password:"
cat /var/lib/jenkins/secrets/initialAdminPassword
echo ""
echo "  NOTE: Restart your SSH session for"
echo "  Docker group permissions to take effect."
echo "========================================"
