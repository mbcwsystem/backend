#!/usr/bin/env bash
set -e

echo "코드 품질 검증을 시작합니다."

# 1) Ruff Lint (fix 없이)
echo "[1/4] Ruff: 코드 스타일 및 버그 패턴 검증 중..."
ruff check app || exit 1

# 2) Ruff Formatter (format 스킵, 대신 diff 검사)
echo "[2/4] Ruff Format: 포맷이 필요한지 검사 중..."
ruff format app --check || exit 1

# 3) Black Check (수정 없이 검증만)
echo "[3/4] Black: 코드 포맷 검증 중..."
black app --check || exit 1

# 4) Mypy (타입 검증)
echo "[4/4] Mypy: 타입 검증 중..."
mypy app || exit 1

echo "모든 코드 검증이 완료되었습니다."