# Dockerfile
FROM python:3.9-slim

# Set working directory in the container.
WORKDIR /app

# Copy all files from your local directory to the container.
COPY output /app/output
COPY ./scripts /app/scripts
COPY ./*.py /app/

RUN useradd -u 1001 -m client
RUN chown -R client:client /app

USER client

# Install external dependencies.
RUN chmod +x scripts/setup.sh
RUN ./scripts/setup.sh
RUN chown -R client:client /app/output
# Command to run the simulation.
ENTRYPOINT [ "/app/.venv/bin/python" ]
