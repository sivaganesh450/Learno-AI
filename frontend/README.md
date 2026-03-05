# Lerno Frontend - React Application

Frontend interface for the Lerno Student Learning Assistant, deployed on **AWS CloudFront + S3**.

## Live URL

https://d8y63sf81k9rq.cloudfront.net

## Local Setup

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Features

- Modern React 19 with Hooks
- React Router for navigation
- Axios for API calls
- JWT authentication
- Responsive design
- Custom Blue, Black, and White theme

## Environment

| File | Variable | Value |
|---|---|---|
| `.env.development` | `VITE_API_URL` | `http://localhost:8000/api/v1` |
| `.env.production` | `VITE_API_URL` | `https://ih2ztarjgh.execute-api.us-east-1.amazonaws.com/demo/api/v1` |

## AWS Deployment

Frontend is hosted on S3 and served via CloudFront:
- **S3 Bucket:** `lerno-frontend-demo`
- **CloudFront Distribution:** `E3ENBK1TY2ST0R` (`d8y63sf81k9rq.cloudfront.net`)
- **403 errors** redirect to `/index.html` for SPA client-side routing

### Redeploying

```bash
npm run build
aws s3 sync dist/ s3://lerno-frontend-demo --delete
aws cloudfront create-invalidation --distribution-id E3ENBK1TY2ST0R --paths "/*"
```

