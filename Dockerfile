# Recipe unvalidated: Docker engine was unavailable on the recorded host.
FROM python:3.13.14-slim
WORKDIR /artifact
COPY requirements.lock requirements-paper.lock ./
RUN pip install --no-cache-dir -r requirements-paper.lock
COPY . .
ENV PYTHONPATH=/artifact/src
CMD ["python", "scripts/tasks.py", "smoke"]
# Invoke with --network none. Full paper/formal builds additionally need
# Java/PRISM/TeX, which are not bundled in this smoke image.
