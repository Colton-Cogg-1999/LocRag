#!/usr/bin/env bash
# OPUS KDE4 v2: matching software-localization corpora; archives remain local.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw/KDE4
for pair in en-es de-en en-zh_CN; do
  destination="data/raw/KDE4/$pair.zip"
  if [[ ! -f "$destination" ]]; then
    curl --fail --location --retry 3 --output "$destination.part" \
      "https://object.pouta.csc.fi/OPUS-KDE4/v2/moses/$pair.txt.zip"
    mv "$destination.part" "$destination"
  fi
  unzip -tq "$destination"
done
