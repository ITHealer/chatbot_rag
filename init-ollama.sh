#!/bin/sh
ollama pull deepseek-r1
exec ollama serve
chmod +x init-ollama.sh