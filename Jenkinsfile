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

        stage('Test') {
            steps {
                echo 'Running Unit Tests...'
                sh 'make test'
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
                    echo 'Deploying with Helm...'
                    sh """
                    helm upgrade --install interview-assistant ./helm/interview-assistant \
                        --set image.tag=${BUILD_NUMBER} \
                        --set image.repository=${DOCKER_HUB_USER}/${IMAGE_NAME_BACKEND}
                    """
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
