# Lerno Backend - FastAPI Server

Backend API for the Lerno Student Learning Assistant, deployed on **AWS Lambda** with **Amazon Bedrock** (Claude 3 Haiku).

## Live API

- **Base URL:** https://ih2ztarjgh.execute-api.us-east-1.amazonaws.com/demo
- **Health Check:** https://ih2ztarjgh.execute-api.us-east-1.amazonaws.com/demo/health

## Local Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (see Environment Variables below)

4. Run server:
```bash
uvicorn main:app --reload --port 8000
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## AWS Deployment

The backend runs on AWS Lambda (Python 3.12) via Mangum:
- **Lambda function:** `lerno-backend` (1024 MB, 300s timeout)
- **API Gateway:** REST API with `{proxy+}` Lambda proxy integration
- **Handler:** `main.handler` (Mangum wraps the FastAPI app)

### Redeploying

```bash
aws s3 cp lambda_deployment.zip s3://lerno-uploads-demo/lambda/lambda_deployment.zip
aws lambda update-function-code --function-name lerno-backend \
  --s3-bucket lerno-uploads-demo --s3-key lambda/lambda_deployment.zip
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `MONGO_URI` | Yes | MongoDB Atlas connection string |
| `DATABASE_NAME` | No | Database name (default: `lerno_db`) |
| `SECRET_KEY` | No | JWT secret key |
| `ALGORITHM` | No | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token TTL (default: `1440`) |
| `TAVILY_API_KEY` | No | Tavily web search API key |
| `AWS_REGION` | No | AWS region (default: `us-east-1`) |
| `S3_UPLOADS_BUCKET` | No | S3 bucket for uploads (default: `lerno-uploads-demo`) |
| `BEDROCK_MODEL_ID` | No | Bedrock model (default: `anthropic.claude-3-haiku-20240307-v1:0`) |

## Key Dependencies

- **fastapi** + **mangum** — ASGI web framework + Lambda adapter
- **langchain-aws** — Amazon Bedrock LLM integration
- **langgraph** — Agentic AI workflow orchestration
- **motor** — Async MongoDB driver
- **boto3** — AWS SDK (Textract, S3, Bedrock)
- **tavily-python** — Web search
- **pypdf** + **python-docx** — Document parsing
- **sympy** — Symbolic math
