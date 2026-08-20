#!/usr/bin/env bash
# Usage: ./gitswitch.sh diva | robert | queen | jessie

USER="${1:-diva}"

case "$USER" in
  diva)
    git config user.name "divapermanaputraid-rgb"
    git config user.email "divapermanaputra.id@gmail.com"
    REMOTE_URL="https://github.com/divapermanaputraid-rgb/python-executor.git"
    REMOTE_NAME="origin-diva"
    ;;
  robert)
    git config user.name "robert-gaarciaa"
    git config user.email "divapermanaputra.sc@gmail.com"
    REMOTE_URL="https://github.com/divapermanaputraid-rgb/python-executor.git"
    REMOTE_NAME="origin-robert"
    ;;
  queen)
    git config user.name "queenzamobile18-cmd"
    git config user.email "queenzamobile18@gmail.com"
    REMOTE_URL="https://github.com/divapermanaputraid-rgb/python-executor.git"
    REMOTE_NAME="origin-queen"
    ;;
  jessie)
    git config user.name "jeessie-rode"
    git config user.email "putradivapermana@gmail.com"
    REMOTE_URL="https://github.com/divapermanaputraid-rgb/python-executor.git"
    REMOTE_NAME="origin-jessie"
    ;;
  *)
    echo "Usage: ./gitswitch.sh diva | robert | queen | jessie"
    exit 1
    ;;
esac

# Add remote if not exists
if ! git remote get-url "$REMOTE_NAME" &>/dev/null; then
  git remote add "$REMOTE_NAME" "$REMOTE_URL"
  echo "Remote '$REMOTE_NAME' added."
fi

echo "Switched to: $(git config user.name) <$(git config user.email)>"
echo "Push target: $REMOTE_NAME → $REMOTE_URL"
