# docker build -t biocommons/seqrepo-rest-service .   (or: make docker-image)

FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# git is required by setuptools_scm to derive the package version
RUN apt-get update && \
    apt-get install --no-install-recommends -y git && \
    rm -rf /var/lib/apt/lists/* && \
    git config --global --add safe.directory /app

WORKDIR /app

# Install dependencies first (cached layer)
COPY uv.lock pyproject.toml /app/
RUN uv sync --frozen --no-dev --no-install-project

# Install the project. The host repo may use git extensions (e.g.,
# relativeWorktrees, git >= 2.48) that the image's git can't read; drop them
# in the copied .git (only) so setuptools_scm can derive the version.
COPY . /app
RUN git config --file .git/config --unset-all extensions.relativeworktrees || true && \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 5000

# Serves $SEQREPO_ROOT_DIR/latest (default /usr/local/share/seqrepo/latest);
# mount a seqrepo root at /usr/local/share/seqrepo, or pass an instance dir.
CMD ["seqrepo-rest-service"]
