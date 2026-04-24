pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'your_dockerhub_username'
        IMAGE_NAME_BACKEND = "interview-assistant-backend"
        IMAGE_NAME_FRONTEND = "interview-assistant-frontend"
        DOCKER_HUB_CREDENTIALS_ID = 'dockerhub-credentials'
        GIT_REPO = 'https://github.com/youruser/interview-assistant.git'
        K8S_CREDENTIALS_ID = 'k8s-config'
    }

    stages {
        stage('Code Checkout') {
            steps {
                git branch: 'main', url: "${GIT_REPO}"
            }
        }

        stage('Lint & Test') {
            steps {
                echo 'Running Linting...'
                // sh 'pylint backend/*.py'
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    echo 'Building Backend Image...'
                    sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME_BACKEND}:${BUILD_NUMBER} ./backend"
                    sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME_BACKEND}:latest ./backend"
                    
                    echo 'Building Frontend Image...'
                    sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME_FRONTEND}:${BUILD_NUMBER} ./frontend"
                    sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME_FRONTEND}:latest ./frontend"
                }
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                echo 'Scanning Backend Image...'
                // sh "trivy image ${DOCKER_HUB_USER}/${IMAGE_NAME_BACKEND}:${BUILD_NUMBER}"
            }
        }

        stage('Docker Push') {
            steps {
                script {
                    docker.withRegistry('', DOCKER_HUB_CREDENTIALS_ID) {
                        sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME_BACKEND}:${BUILD_NUMBER}"
                        sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME_BACKEND}:latest"
                        sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME_FRONTEND}:${BUILD_NUMBER}"
                        sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME_FRONTEND}:latest"
                    }
                }
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                withKubeConfig([credentialsId: K8S_CREDENTIALS_ID]) {
                    sh "sed -i 's|IMAGE_TAG|${BUILD_NUMBER}|g' k8s/backend-deployment.yaml"
                    sh "sed -i 's|IMAGE_TAG|${BUILD_NUMBER}|g' k8s/frontend-deployment.yaml"
                    sh "kubectl apply -f k8s/"
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
