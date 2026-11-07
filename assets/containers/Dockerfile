# SPARMVET-VIZ — Production Container
#
# Includes:
#   - Python 3.12 + all app dependencies (from pyproject.toml)
#   - Quarto (for report rendering: HTML, PDF, DOCX)
#   - LuaLaTeX via texlive-luatex (for PDF output)
#   - Pandoc (bundled with Quarto)
#
# --- Source ---
# Currently the repo is COPY'd into the image at build time.
# TODO: switch to a tagged release once a release workflow exists, e.g.:
#   ARG REPO_TAG=v1.0.0
#   RUN git clone --depth 1 --branch ${REPO_TAG} \
#       https://github.com/your-org/sparmvet-viz.git /app
# For now: docker build -t sparmvet-viz:latest -f assets/containers/Dockerfile .
# (run from repo root so the build context is the full repo)
#
# --- Run (filesystem connector, developer app features) ---
#   docker run --rm -p 8001:8001 \
#     -v /data/my_project:/data \
#     -e SPARMVET_DEPLOYMENT=/data/deployment.yaml \
#     sparmvet-viz:latest
#
# --- Run (pipeline mode, static app features, data injected via volume) ---
#   docker run --rm -p 8001:8001 \
#     -v /pipeline/output:/pipeline/output:ro \
#     -v /pipeline/config:/app/config/deployment/pipeline:ro \
#     -e SPARMVET_DEPLOYMENT=/app/config/deployment/pipeline/deployment.yaml \
#     -e SPARMVET_APP_FEATURES=/app/config/app_features/pipeline-static.yaml \
#     sparmvet-viz:latest

FROM python:3.12-slim

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ca-certificates \
    # LaTeX for Quarto PDF rendering
    texlive-luatex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-plain-generic \
    texlive-latex-extra \
    lmodern \
    # SVG→PDF transcoding for Quarto PDF output (rsvg-convert)
    librsvg2-bin \
    # libGL for plotnine/matplotlib SVG/PDF backends
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Quarto ────────────────────────────────────────────────────────────────────
# Pin version for reproducibility; update as needed.
ARG QUARTO_VERSION=1.8.27
RUN wget -qO /tmp/quarto.deb \
    "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb" \
    && dpkg -i /tmp/quarto.deb \
    && rm /tmp/quarto.deb

# ── App ───────────────────────────────────────────────────────────────────────
WORKDIR /app

# Copy the full repo (build context = repo root)
# TODO: replace with `git clone --depth 1 --branch <tag>` once releases exist
COPY . .

# Install external dependencies from root pyproject.toml,
# then install all local libs (each has its own pyproject.toml).
# pip resolves versions once; no manual dependency list to maintain.
# REVIEW : verify if it uses the toml files for dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && pip install --no-cache-dir \
        libs/viz_factory \
        libs/viz_gallery \
        libs/transformer \
        libs/ingestion \
        libs/generator_utils \
        libs/utils \
        libs/connector

# ── Runtime ───────────────────────────────────────────────────────────────────
ENV PYTHONPATH=/app

# REVIEW : does this allows the user to map to another port 
EXPOSE 8001

CMD ["python", "-m", "shiny", "run", "app/src/main.py", \
     "--host", "0.0.0.0", "--port", "8001"]
