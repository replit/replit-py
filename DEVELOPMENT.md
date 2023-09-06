# Upgrade protobufs

In order to upgrade the protobuf definitions, the following script can be used.

```shell
#!/bin/bash

set -e

GOVAL_DIR="${GOVAL_DIR:-${HOME}/goval}"
WORK_DIR="$(mktemp -d)"

function cleanup {
  rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

# Download the latest protobuf binaries.
curl -sSL https://github.com/protocolbuffers/protobuf/releases/download/v24.2/protoc-24.2-linux-x86_64.zip -o "${WORK_DIR}/protoc.zip"
(cd "${WORK_DIR}" && unzip protoc.zip)
mkdir -p "${WORK_DIR}/replit/goval"

rsync \
  -Lazr \
  --exclude='api/npm' \
  --include='*/' \
  --include='*.proto' \
  --exclude='*' \
  "${GOVAL_DIR}/api" \
  "${WORK_DIR}/replit/goval"
find "${WORK_DIR}" -name '*.proto' | xargs sed -i 's@import "api/@import "replit/goval/api/@g'
"${WORK_DIR}/bin/protoc" \
  -I="${WORK_DIR}" \
  --python_out=src/ \
  "${WORK_DIR}/replit/goval/api/signing.proto" \
  "${WORK_DIR}/replit/goval/api/client.proto" \
  "${WORK_DIR}/replit/goval/api/repl/repl.proto" \
  "${WORK_DIR}/replit/goval/api/features/features.proto"
```
