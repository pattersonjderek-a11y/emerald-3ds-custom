# Build the historical SDK first: docker build -f tools/stage_a.Dockerfile -t emerald-stage-a-sdk .
FROM python:3.13.17-slim-bookworm AS python
FROM emerald-stage-a-sdk
# v0.5.0 pins its generator interpreter separately from the unchanged ARM SDK.
COPY --from=python /usr/local /usr/local
RUN --mount=type=secret,id=proxy_ca,target=/run/proxy-ca.pem \
    stage_e_ca=/etc/ssl/certs/ca-certificates.crt; \
    if [ -f /run/proxy-ca.pem ]; then stage_e_ca=/run/proxy-ca.pem; fi; \
    PIP_CERT="$stage_e_ca" python3 -m pip install --no-cache-dir Pillow==12.3.0
WORKDIR /workspace/emerald-3ds-stage-e
