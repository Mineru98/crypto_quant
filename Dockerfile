# Base image
FROM jupyter/pyspark-notebook:latest

# Install additional dependencies if needed
RUN pip install --no-cache-dir findspark

# Set up environment variables
ENV SPARK_HOME=/usr/local/spark
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=jupyter
ENV PYSPARK_DRIVER_PYTHON_OPTS="notebook --ip='*' --port=8888 --no-browser --allow-root"

# Expose Jupyter Notebook port
EXPOSE 8888
