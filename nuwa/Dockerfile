FROM python:3.14.2-alpine3.23
RUN pip install --no-cache-dir uv
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY pyproject.toml uv.lock .
RUN uv add uwsgi
RUN uv sync
COPY . .
RUN chmod +x /code/wait-for-it.sh
RUN chmod +x /code/entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]