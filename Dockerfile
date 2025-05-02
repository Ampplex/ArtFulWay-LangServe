# Use official AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR /var/task

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --target .

# Copy app code
COPY app.py .
COPY retrieval_pipeline.py .
COPY connection.py .
COPY custom_embeddings.py .
COPY getProjectDocument.py .

# Define Lambda handler
CMD ["app.handler"]
