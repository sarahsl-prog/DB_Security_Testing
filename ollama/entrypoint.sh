#!/bin/bash
/bin/ollama serve &
sleep 10

echo "Pulling base models..."
ollama pull llama3.2:3b
ollama pull qwen2.5-coder:3b
ollama pull qwen3:4b

echo "Creating custom SQL models..."
ollama create llama-sql -f /modelfiles/ModelFile_llama32.txt
ollama create qwen-coder-sql -f /modelfiles/ModelFile_qwen25-coder.txt
ollama create qwen3-sql -f /modelfiles/ModelFile_qwen3:0.6b.txt

echo "All models ready!"
wait
