# Official SDK, frozen to the image actually used for Stage A.
FROM devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5
# Supply a combined CA bundle through --secret id=proxy_ca when behind a
# session proxy. The certificate never becomes an image layer.
RUN --mount=type=secret,id=proxy_ca,target=/run/proxy-ca.pem \
    set -eu; \
    rm -f /etc/apt/sources.list.d/devkitpro.list; \
    stage_a_ca=/etc/ssl/certs/ca-certificates.crt; \
    if [ -f /run/proxy-ca.pem ]; then stage_a_ca=/run/proxy-ca.pem; fi; \
    apt-get -o Acquire::https::CaInfo="$stage_a_ca" update && \
    apt-get -o Acquire::https::CaInfo="$stage_a_ca" install -y --no-install-recommends \
    build-essential=12.9 g++=4:12.2.0-3 libpng-dev=1.6.39-2+deb12u6 \
    python3=3.11.2-1+b1 python3-pil=9.4.0-1.1+deb12u1 \
    git=1:2.39.5-0+deb12u3 && rm -rf /var/lib/apt/lists/*
WORKDIR /project
