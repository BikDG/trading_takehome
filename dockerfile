
# Dockerfile
FROM python:3.9-slim

# Set working directory in the container.
WORKDIR /app

# Copy all files from your local directory to the container.
COPY ./scripts /app/scripts
COPY ./*.py /app/

#Create output folder
RUN mkdir /app/output

#Create client user and switch to it
RUN useradd -u 1001 -m client
RUN chown -R client:client /app
USER client

# Install external dependencies.
RUN chmod +x scripts/setup.sh
RUN ./scripts/setup.sh
RUN chown -R client:client /app/output

#CMD ["./main_dist/main"]

# Command to run the simulation.
ENTRYPOINT ["bash", "-c"]
CMD ["/app/.venv/bin/python main.py | tee /app/output/trading.log"]
