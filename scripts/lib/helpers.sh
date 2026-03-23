#!/bin/bash

set -e

# =======================
# Styling
# =======================
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
BOLD="\033[1m"
RESET="\033[0m"

# =======================
# Helpers
# =======================
log() {
  echo ""
  echo -e "${BLUE}${BOLD}▶ $1${RESET}"
}

success() {
  echo -e "${GREEN}✔ $1${RESET}"
}

warn() {
  echo -e "${YELLOW}⚠ $1${RESET}"
}

error() {
  echo -e "${RED}✖ $1${RESET}"
  exit 1
}

on_error() {
  error "Something went wrong at line $1"
  exit 1
}

trap 'on_error $LINENO' ERR
trap 'warn "Interrupted by user"; exit 130' INT
