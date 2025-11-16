FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libgsl-dev \
    git \
    curl \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN python3 -m pip install \
    numpy \
    scipy \
    matplotlib \
    pandas \
    astropy \
    scikit-learn \
    anthropic \
    openai \
    scikit-image \
    seaborn \
    datasets \
    plotly \
    sympy \
    networkx \
    numba \
    h5py \
    tqdm \
    pyyaml \
    toml \
    requests \
    filelock

RUN python3 -m pip install torch --index-url https://download.pytorch.org/whl/cu126 tensorflow

RUN python3 -m pip install inspect-ai

RUN python3 -m pip install \
    jupyter \
    ipython \
    black \
    pytest

ENV LC_ALL=C
ENV PATH=/usr/local/bin:$PATH