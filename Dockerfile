FROM python:3.9-slim
WORKDIR /workspace
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
