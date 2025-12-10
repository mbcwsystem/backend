#!/usr/bin/env bash
set -e

echo "코드 포맷을 시작합니다."

# 1) Ruff (Lint + isort)
echo "[1/5] 코드 스타일 & 버그 패턴 검사를 시작합니다."
ruff check app --fix || exit 1

# 2) Ruff Formatter
echo "[2/5] 코드 포매터를 시작합니다."
ruff format app || exit 1

# 3) Black Check
echo "[3/5] 코드 포맷 검사를 시작합니다."
black app --check || exit 1

# 4) Mypy
echo "[4/5] 타입 검사를 시작합니다"
mypy app || exit 1

echo "[5/5] 모든 검사가 완료되었습니다."