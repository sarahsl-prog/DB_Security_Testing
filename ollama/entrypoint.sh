#!/bin/bash
/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama server to start
until ollama list &> /dev/null; do
    echo "Waiting for Ollama server to start..."
    sleep 2
done

echo "Pulling base models..."
ollama pull llama3.2:3b
ollama pull qwen3:4b
ollama pull qwen2.5-code:3b

echo "Creating custom SQL models..."
ollama create llama-sql -f /modelfiles/ModelFile_llama32.txt
ollama create qwen3-sql -f /modelfiles/ModelFile_qwen3:4b.txt
ollama create qwen-code-sql -f /modelfiles/ModelFile_qwen25-coder.txt

echo "All models created!"
echo "Loading qwen-coder-sql model to warm up..."
ollama generate qwen-code-sql --prompt "SELECT * FROM users;" --max-tokens 10 > /dev/null 2>&1
echo "Warm-up complete."

wait
