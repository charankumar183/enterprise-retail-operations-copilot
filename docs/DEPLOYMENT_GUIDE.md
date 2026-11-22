# Enterprise AI Retail Operations Copilot: Deployment Guide

This guide details the steps to deploy the application locally via Docker and Nginx, or to public cloud providers (AWS, Azure, Google Cloud).

---

## 1. Local Containerized Deployment (Docker & Nginx)

### Prerequisites:
- Docker Engine $\ge 20.10$
- Docker Compose $\ge 2.0$

### Step-by-Step Execution:
1. Navigate to the project root directory:
   ```bash
   cd "ML PROJECT_3"
   ```
2. Build the multi-stage Docker container:
   ```bash
   docker-compose -f docker/docker-compose.yml build
   ```
3. Launch the containerized application and Nginx reverse proxy:
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```
4. Verify container health:
   ```bash
   docker ps
   curl -f http://localhost:8000/health
   ```
5. Access the application:
   - **Frontend UI & Dashboard:** `http://localhost/` (via Nginx port 80) or `http://localhost:8000/`
   - **Interactive API Swagger Docs:** `http://localhost:8000/docs`

---

## 2. Public Cloud Deployment (AWS, Azure, GCP)

### Option A: AWS Elastic Container Service (ECS Fargate) or App Runner
1. **ECR Repository Setup:**
   ```bash
   aws ecr create-repository --repository-name enterprise-retail-copilot --region us-east-1
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
   ```
2. **Build, Tag & Push Image:**
   ```bash
   docker build -t enterprise-retail-copilot -f docker/Dockerfile .
   docker tag enterprise-retail-copilot:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/enterprise-retail-copilot:latest
   docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/enterprise-retail-copilot:latest
   ```
3. **AWS App Runner Deployment:**
   - Source: ECR Container image.
   - Port: `8000`.
   - Environment variables: Load from `.env`.
   - App Runner provisions an HTTPS load-balanced endpoint (e.g. `https://xxxxxx.us-east-1.awsapprunner.com`).

### Option B: Google Cloud Run
1. **Build and Submit via Google Cloud Build:**
   ```bash
   gcloud builds submit --tag gcr.io/<PROJECT-ID>/enterprise-retail-copilot
   ```
2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy retail-copilot \
     --image gcr.io/<PROJECT-ID>/enterprise-retail-copilot \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8000 \
     --memory 2Gi \
     --cpu 2
   ```
3. Google Cloud Run automatically generates a verified HTTPS endpoint.

### Option C: Azure Container Apps (ACA)
1. **Azure Container Registry & ACA Deploy:**
   ```bash
   az acr build --registry <registry_name> --image retail-copilot:v1 .
   az containerapp create \
     --name retail-copilot-app \
     --resource-group retail-rg \
     --environment retail-env \
     --image <registry_name>.azurecr.io/retail-copilot:v1 \
     --target-port 8000 \
     --ingress external
   ```

---

## 3. External Deployment Status Notice

Per project guidelines:
- If cloud credentials (AWS Access Keys, Azure Service Principal, GCP Service Account) are not provided in the local environment, the application is fully containerized, locally verified, and deployment-ready.
- A public cloud deployment requires executing the 3 cloud commands above using active provider credentials to generate a verified public URL.
