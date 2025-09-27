FROM python:3.10-bookworm

WORKDIR /usr/src/code_safe
COPY . .
RUN pip install --no-cache-dir .

ENTRYPOINT [ "code_safe" ]
