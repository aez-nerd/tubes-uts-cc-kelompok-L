pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = 'tubesutscc'
        BACKEND_IMAGE = 'team-task-backend:latest'
    }

    stages {
        // STAGE 1: Mengambil kode terbaru dari repositori GitHub
        stage('Checkout') {
            steps {
                echo '=== [Stage 1/5] Checkout Source Code dari GitHub ==='
                checkout scm
            }
        }

        // STAGE 2: Memeriksa sintaks kode Python & konfigurasi Docker Compose
        stage('Syntax Check') {
            steps {
                echo '=== [Stage 2/5] Memeriksa Sintaks app.py & docker-compose.yml ==='
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m py_compile app.py
                            docker compose config -q
                        '''
                    } else {
                        bat '''
                            docker run --rm -v "%CD%:/app" -w /app python:3.11-slim python -m py_compile app.py
                            docker compose config -q
                        '''
                    }
                }
            }
        }

        // STAGE 3: Membangun Docker Image untuk Backend Service
        stage('Build Image') {
            steps {
                echo '=== [Stage 3/5] Membangun Docker Image Backend ==='
                script {
                    if (isUnix()) {
                        sh 'docker compose build'
                    } else {
                        bat 'docker compose build'
                    }
                }
            }
        }

        // STAGE 4: Menjalankan kontainer dengan Docker Compose (Named Volume tetap aman)
        stage('Automated Deployment') {
            steps {
                echo '=== [Stage 4/5] Menjalankan Deployment Kontainer (Frontend & Backend) ==='
                script {
                    if (isUnix()) {
                        sh '''
                            if [ -d "/host_project" ]; then
                                cp -f index.html app.py Dockerfile docker-compose.yml /host_project/ || true
                            fi
                            docker rm -f team-task-frontend team-task-backend || true
                            docker compose up -d
                            docker cp index.html team-task-frontend:/usr/share/nginx/html/index.html || true
                            docker exec team-task-frontend chmod -R 755 /usr/share/nginx/html || true
                        '''
                    } else {
                        bat '''
                            docker rm -f team-task-frontend team-task-backend
                            docker compose up -d
                        '''
                    }
                }
            }
        }

        // STAGE 5: Memastikan layanan Backend & Frontend berjalan sehat (HTTP 200 OK)
        stage('Health Check') {
            steps {
                echo '=== [Stage 5/5] Memeriksa Kesehatan Layanan (Health Check) ==='
                script {
                    sleep(time: 3, unit: 'SECONDS')
                    if (isUnix()) {
                        sh '''
                            docker ps
                            docker exec team-task-backend python -c "import urllib.request; res = urllib.request.urlopen('http://127.0.0.1:5000/tasks'); assert res.status == 200; print('Backend API OK:', res.read().decode())"
                            docker exec team-task-frontend wget -qO- http://127.0.0.1:80 > /dev/null && echo "Frontend Nginx OK (HTTP 200)"
                        '''
                    } else {
                        bat '''
                            docker ps
                            docker exec team-task-backend python -c "import urllib.request; res = urllib.request.urlopen('http://127.0.0.1:5000/tasks'); assert res.status == 200; print('Backend API OK:', res.read().decode())"
                            docker exec team-task-frontend wget -qO- http://127.0.0.1:80 > NUL && echo Frontend Nginx OK (HTTP 200)
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline CI/CD Berhasil! Aplikasi Papan Catatan Tugas Kelompok telah ter-deploy.'
        }
        failure {
            echo '❌ Pipeline CI/CD Gagal. Silakan periksa log error pada stage di atas.'
        }
    }
}
