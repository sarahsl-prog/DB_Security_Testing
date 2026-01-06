# List available models
curl http://localhost:11434/api/tags

# Show running models
curl http://localhost:11434/api/ps

# Model information
curl http://localhost:11434/api/show -d '{
  "name": "deepseek-coder:1.3b"
}'

# Simple generation test
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-coder:1.3b",
  "prompt": "Write SQL to select all patients",
  "stream": false
}'

# Test from remote host (Frontend/Backend)
curl http://192.168.1.12:11434/api/generate -d '{
  "model": "deepseek-coder:1.3b",
  "prompt": "SELECT * FROM patients",
  "stream": false
}'


# Chat completion test
curl http://localhost:11434/api/chat -d '{
  "model": "deepseek-coder:1.3b",
  "messages": [
    {
      "role": "system",
      "content": "You are a SQL expert."
    },
    {
      "role": "user",
      "content": "Generate SQL to find all patients with last name Smith"
    }
  ],
  "stream": false
}'