FROM ollama/ollama
COPY modelfiles/ /modelfiles/
RUN ollama serve & sleep 5 && \
ollama pull qwen2.5-coder:3b && \
ollama create qwen-coder-sql -f /modelfiles/ModelFile_qwen25-coder.txt && \
pkill ollama
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
