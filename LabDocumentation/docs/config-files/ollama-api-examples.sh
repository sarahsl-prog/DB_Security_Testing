# List available models
curl http://localhost:11434/api/tags

# Show running models
curl http://localhost:11434/api/ps

# Model information
curl http://localhost:11434/api/show -d '{
  "name": "qwen2.5-coder"
}'

# Simple generation test
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder",
  "prompt": "Write SQL to select all patients",
  "stream": false
}'

# Test from remote host (Frontend/Backend)
curl http://192.168.1.12:11434/api/generate -d '{
  "model": "qwen2.5-coder",
  "prompt": "SELECT * FROM patients",
  "stream": false
}'


# Chat completion test
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5-coder",
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