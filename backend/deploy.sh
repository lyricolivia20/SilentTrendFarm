#!/bin/bash

# Deployment script for backend
echo "🚀 Deploying SilentTrendFarm Backend"
echo "====================================="

# Check if .env exists
if [ ! -f ../.env ]; then
    echo "❌ Error: .env file not found. Copy .env.example and configure it."
    exit 1
fi

# Load environment variables
export $(cat ../.env | grep -v '^#' | xargs)

# Select deployment target
echo "Select deployment target:"
echo "1) Railway"
echo "2) Render"
echo "3) Fly.io"
echo "4) DigitalOcean App Platform"
echo "5) Google Cloud Run"
echo "6) AWS Lambda (Serverless)"
echo "7) Docker Hub"
read -p "Enter choice (1-7): " choice

case $choice in
    1)
        echo "📦 Deploying to Railway..."
        # Railway deployment
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi
        railway login
        railway init
        railway up
        ;;
    2)
        echo "📦 Deploying to Render..."
        # Create render.yaml if not exists
        cat > ../render.yaml << EOF
services:
  - type: web
    name: silenttrendfarm-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port \$PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
EOF
        echo "✅ render.yaml created. Push to GitHub and connect on render.com"
        ;;
    3)
        echo "📦 Deploying to Fly.io..."
        if ! command -v flyctl &> /dev/null; then
            echo "Installing Fly CLI..."
            curl -L https://fly.io/install.sh | sh
        fi
        flyctl launch --dockerfile Dockerfile
        flyctl deploy
        ;;
    4)
        echo "📦 Deploying to DigitalOcean App Platform..."
        # Create app spec
        cat > ../app.yaml << EOF
name: silenttrendfarm-backend
services:
- name: api
  github:
    repo: YOUR_GITHUB_REPO
    branch: main
    deploy_on_push: true
  source_dir: backend
  dockerfile_path: backend/Dockerfile
  http_port: 8000
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /api
EOF
        echo "✅ app.yaml created. Use 'doctl apps create --spec app.yaml'"
        ;;
    5)
        echo "📦 Deploying to Google Cloud Run..."
        gcloud run deploy silenttrendfarm-backend \
            --source . \
            --port 8000 \
            --allow-unauthenticated \
            --region us-central1
        ;;
    6)
        echo "📦 Creating AWS Lambda deployment package..."
        # Install dependencies in a directory
        pip install -r ../requirements.txt -t lambda_package/
        cp main.py lambda_package/
        cd lambda_package
        zip -r ../lambda_deployment.zip .
        cd ..
        echo "✅ lambda_deployment.zip created. Upload to AWS Lambda"
        ;;
    7)
        echo "📦 Building and pushing to Docker Hub..."
        read -p "Enter Docker Hub username: " docker_user
        docker build -t $docker_user/silenttrendfarm-backend:latest .
        docker push $docker_user/silenttrendfarm-backend:latest
        echo "✅ Pushed to Docker Hub: $docker_user/silenttrendfarm-backend:latest"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo "✅ Deployment complete!"
