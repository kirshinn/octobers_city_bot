#!/bin/bash
# deploy.sh - автоматическое развертывание бота на k3s

REPO_ROOT=$(pwd)
K8S_DIR="$REPO_ROOT/k8s"
VOLUME_DIR="/home/k3s-volumes/octobers-city-bot"
SECRET_FILE="$K8S_DIR/secret.yaml"

# Читаем токен из .env
if [ ! -f "$REPO_ROOT/.env" ]; then
    echo ".env не найден в корне репозитория!"
    exit 1
fi

BOT_TOKEN=$(grep BOT_TOKEN "$REPO_ROOT/.env" | cut -d '=' -f2-)
if [ -z "$BOT_TOKEN" ]; then
    echo "BOT_TOKEN пустой в .env"
    exit 1
fi

# Создаём директорию для SQLite, если нужно
mkdir -p "$VOLUME_DIR"
touch "$VOLUME_DIR/users.db"
chmod 600 "$VOLUME_DIR/users.db"

# Генерируем secret.yaml с токеном
cat > "$SECRET_FILE" <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: octobers-city-bot-secret
  namespace: default
type: Opaque
stringData:
  BOT_TOKEN: "$BOT_TOKEN"
EOF

# Применяем манифесты
kubectl apply -f "$SECRET_FILE"
kubectl apply -f "$K8S_DIR/configmap.yaml"
kubectl apply -f "$K8S_DIR/deployment.yaml"

# Опционально для вебхуков
# kubectl apply -f "$K8S_DIR/service.yaml"

echo "Бот развернут. SQLite: $VOLUME_DIR/users.db"
