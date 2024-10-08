# 最初に構築したイメージと合わせる
FROM python:3.10-slim
WORKDIR /app

# お好みで好きなパッケージを追加
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global --add safe.directory /app

# poetryのインストール
RUN pip install --upgrade pip && pip install poetry 
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

COPY ./pyproject.toml ./poetry.lock* ./
RUN poetry install \
    && poetry export -f requirements.txt -o requirements.txt --without-hashes



# ユーザーIDとグループIDをビルド時の引数として受け取る
ARG USER_ID=1000
ARG GROUP_ID=1000

# ユーザーとグループを作成
RUN groupadd -g ${GROUP_ID} appgroup && \
    useradd -m -d /home/appuser -s /bin/bash -u ${USER_ID} -g appgroup appuser && \
    echo 'appuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV HOME=/home/appuser
USER appuser