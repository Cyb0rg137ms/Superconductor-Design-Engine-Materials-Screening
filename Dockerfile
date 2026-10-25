FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY scdesign ./scdesign
COPY materials ./materials
RUN pip install --no-cache-dir ".[plot]"
ENTRYPOINT ["scdesign"]
CMD ["bench", "--quick", "--out", "/tmp/bench"]
