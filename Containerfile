# syntax=docker/dockerfile:1
#
# This project depends on pylegifrance via a local editable path (see
# pyproject.toml's [tool.uv.sources]) while https://github.com/jfenal/pylegifrance's
# fixes aren't merged upstream. Rather than widening the build context to the
# parent directory (which would make .dockerignore below silently inert --
# both engines only honor an ignore-file at the actual context root),
# pylegifrance is brought in as a named secondary build context. Requires
# Podman 4.1+ or Docker 23+ / Buildx (both support --build-context).
#
#   git clone https://github.com/jfenal/legifrance-mcp.git
#   git clone -b direct-piste-integration https://github.com/jfenal/pylegifrance.git
#
#   # podman finds "Containerfile" by name automatically:
#   podman build --build-context pylegifrance=./pylegifrance -t legifrance-mcp legifrance-mcp
#
#   # docker needs -f, since it defaults to looking for "Dockerfile":
#   docker build -f legifrance-mcp/Containerfile --build-context pylegifrance=./pylegifrance -t legifrance-mcp legifrance-mcp
#
# Run with your PISTE credentials (see README.md's Installation section):
#
#   podman run --rm -i --env-file legifrance-mcp/.env legifrance-mcp

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /build

COPY --from=pylegifrance . ./pylegifrance
COPY pyproject.toml uv.lock ./legifrance-mcp/

WORKDIR /build/legifrance-mcp
RUN uv sync --locked --no-dev

COPY src ./src

# Claude Desktop and other MCP clients speak stdio to this process -- run it
# with `podman run -i`/`docker run -i` (interactive, no allocated tty) so
# stdin/stdout stay a clean byte stream for the MCP protocol.
#
# --no-sync: `uv run` otherwise re-syncs against the full lockfile (dev
# group included) on every start, silently undoing --no-dev above and
# pulling ~90MB of dev-only tooling (mypy, basedpyright, nodejs-wheel-binaries)
# over the network at container startup. The venv built above already has
# exactly what's needed.
ENTRYPOINT ["uv", "run", "--no-sync", "python", "src/server.py"]
