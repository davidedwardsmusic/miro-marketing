# Secrets Setup Guide

This project uses local configuration files that contain secrets and should NOT be committed to git.

## Files with Secrets (Not Committed)

The following files are in `.gitignore` and will NOT be pushed to GitHub:

- `Dockerfile` - Contains environment variables with API keys
- `secrets-values.yaml` - Contains Kubernetes secrets for Helm deployment

## Template Files (Committed)

Template versions of these files are provided in the repository:

- `Dockerfile.template` - Template for Docker configuration
- `secrets-values.yaml.template` - Template for Kubernetes secrets

## Setup Instructions

### First Time Setup

1. **Copy the template files:**
   ```bash
   cp Dockerfile.template Dockerfile
   cp secrets-values.yaml.template secrets-values.yaml
   ```

2. **Edit the files and add your actual secrets:**
   
   **Dockerfile:**
   ```dockerfile
   ENV MIRO_API_TOKEN=your_actual_miro_token_here
   ENV OPENAI_API_KEY=your_actual_openai_key_here
   ENV MIRO_BOARD_ID=your_board_id_here
   ```
   
   **secrets-values.yaml:**
   ```yaml
   secrets:
     openaiApiKey: "your_actual_openai_key_here"
     miroApiToken: "your_actual_miro_token_here"
   ```

3. **Verify the files are ignored:**
   ```bash
   git check-ignore -v Dockerfile secrets-values.yaml
   ```
   
   You should see output confirming both files are ignored.

## Important Notes

- ✅ The actual `Dockerfile` and `secrets-values.yaml` files exist locally but are NOT tracked by git
- ✅ You can edit these files freely without worrying about committing secrets
- ✅ Template files are committed so other developers know what configuration is needed
- ⚠️ Never remove these entries from `.gitignore`
- ⚠️ If you accidentally commit secrets, you must revoke the API keys immediately

## Alternative: Using .env File

For local development, you can also use a `.env` file (already in `.gitignore`):

```bash
MIRO_API_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
MIRO_BOARD_ID=your_board_id_here
OPENAI_MODEL=gpt-4
```

The application will automatically load these environment variables.

## Deployment

For production deployments:

- **Docker:** Pass secrets via environment variables at runtime
  ```bash
  docker run -e OPENAI_API_KEY="..." -e MIRO_API_TOKEN="..." your-image
  ```

- **Kubernetes/Helm:** Use the `secrets-values.yaml` file with Helm
  ```bash
  helm install miro-marketing ./helm/miro-marketing -f secrets-values.yaml
  ```

- **GitHub Actions:** Store secrets in GitHub repository settings → Secrets and variables → Actions

