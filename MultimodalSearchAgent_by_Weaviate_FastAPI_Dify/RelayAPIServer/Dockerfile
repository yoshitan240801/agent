FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi==0.136.3
RUN pip install --no-cache-dir uvicorn[standard]==0.34.3
RUN pip install --no-cache-dir pydantic==2.13.4
RUN pip install --no-cache-dir weaviate-client==4.21.0
RUN pip install --no-cache-dir python-dotenv==1.1.1
RUN pip install --no-cache-dir packaging==25.0

COPY ./work /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10002", "--reload"]