FROM python:3.10-slim

# お好みで好きなパッケージを追加
RUN apt-get update && apt-get install -y \
build-essential \
git \
curl \
sudo \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

RUN git config --global --add safe.directory /app


# ユーザーIDとグループIDをビルド時の引数として受け取る
ARG USER_ID=1000
ARG GROUP_ID=1000

# ユーザーとグループを作成
RUN groupadd -g ${GROUP_ID} appgroup && \
useradd -m -d /home/appuser -s /bin/bash -u ${USER_ID} -g appgroup appuser && \
echo 'appuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV HOME=/home/appuser
USER appuser


WORKDIR /app

# poetryのインストール
RUN pip install --upgrade pip && pip install poetry 
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

COPY --chown=appuser:appgroup pyproject.toml poetry.lock ./
RUN poetry install \
    && poetry export -f requirements.txt -o requirements.txt --without-hashes


# アプリケーションコードをコピー
COPY --chown=appuser:appgroup . /app