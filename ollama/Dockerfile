FROM ollama/ollama
COPY modelfiles/ /modelfiles/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
