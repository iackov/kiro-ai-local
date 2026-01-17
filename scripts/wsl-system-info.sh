#!/bin/bash
# -*- coding: utf-8 -*-
# Сбор информации о системе через WSL (Ubuntu)

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "\n${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       🐧 ИНФОРМАЦИЯ О СИСТЕМЕ ЧЕРЕЗ WSL (Ubuntu) 🐧       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Создать директорию для отчётов
mkdir -p /mnt/c/Users/Jack/source/kiro-ai-local/generated

# Файл для отчёта
REPORT="/mnt/c/Users/Jack/source/kiro-ai-local/generated/wsl-system-info.md"

# Начало отчёта
cat > "$REPORT" << EOF
# 🐧 Отчёт о системе через WSL (Ubuntu)

**Дата создания**: $(date '+%Y-%m-%d %H:%M:%S')

---

EOF

echo -e "${YELLOW}📊 Сбор информации через WSL...${NC}\n"

# WSL информация
echo -e "${CYAN}🐧 WSL${NC}"
echo "## 🐧 WSL" >> "$REPORT"
echo "" >> "$REPORT"

WSL_VERSION=$(cat /proc/version | grep -oP 'WSL\d+' || echo "WSL")
DISTRO=$(lsb_release -d | cut -f2)
KERNEL=$(uname -r)

echo "  Версия: $WSL_VERSION"
echo "  Дистрибутив: $DISTRO"
echo "  Ядро: $KERNEL"

echo "- **Версия**: $WSL_VERSION" >> "$REPORT"
echo "- **Дистрибутив**: $DISTRO" >> "$REPORT"
echo "- **Ядро**: $KERNEL" >> "$REPORT"
echo "" >> "$REPORT"

# Процессор
echo -e "\n${CYAN}🔧 Процессор${NC}"
echo "## 🔧 Процессор" >> "$REPORT"
echo "" >> "$REPORT"

CPU_MODEL=$(lscpu | grep "Model name" | cut -d: -f2 | xargs)
CPU_CORES=$(nproc)
CPU_THREADS=$(lscpu | grep "^CPU(s):" | awk '{print $2}')

echo "  Модель: $CPU_MODEL"
echo "  Ядер: $CPU_CORES"
echo "  Потоков: $CPU_THREADS"

echo "- **Модель**: $CPU_MODEL" >> "$REPORT"
echo "- **Ядер**: $CPU_CORES" >> "$REPORT"
echo "- **Потоков**: $CPU_THREADS" >> "$REPORT"
echo "" >> "$REPORT"

# Память
echo -e "\n${CYAN}💾 Память${NC}"
echo "## 💾 Память" >> "$REPORT"
echo "" >> "$REPORT"

TOTAL_MEM=$(free -h | grep Mem | awk '{print $2}')
USED_MEM=$(free -h | grep Mem | awk '{print $3}')
FREE_MEM=$(free -h | grep Mem | awk '{print $4}')

echo "  Всего: $TOTAL_MEM"
echo "  Используется: $USED_MEM"
echo "  Свободно: $FREE_MEM"

echo "- **Всего**: $TOTAL_MEM" >> "$REPORT"
echo "- **Используется**: $USED_MEM" >> "$REPORT"
echo "- **Свободно**: $FREE_MEM" >> "$REPORT"
echo "" >> "$REPORT"

# Диски (Windows диски через /mnt)
echo -e "\n${CYAN}💿 Диски Windows (через /mnt)${NC}"
echo "## 💿 Диски Windows" >> "$REPORT"
echo "" >> "$REPORT"

for drive in /mnt/*; do
    if [ -d "$drive" ]; then
        DRIVE_NAME=$(basename "$drive")
        DISK_INFO=$(df -h "$drive" 2>/dev/null | tail -1)
        if [ ! -z "$DISK_INFO" ]; then
            SIZE=$(echo "$DISK_INFO" | awk '{print $2}')
            USED=$(echo "$DISK_INFO" | awk '{print $3}')
            AVAIL=$(echo "$DISK_INFO" | awk '{print $4}')
            PERCENT=$(echo "$DISK_INFO" | awk '{print $5}')
            
            echo "  $DRIVE_NAME: $SIZE всего, $USED используется ($PERCENT)"
            echo "- **$DRIVE_NAME**: $SIZE всего, $USED используется ($PERCENT)" >> "$REPORT"
        fi
    fi
done

echo "" >> "$REPORT"

# Docker (если доступен из WSL)
echo -e "\n${CYAN}🐳 Docker${NC}"
echo "## 🐳 Docker" >> "$REPORT"
echo "" >> "$REPORT"

if command -v docker &> /dev/null; then
    DOCKER_VER=$(docker --version 2>/dev/null)
    if [ $? -eq 0 ]; then
        CONTAINERS=$(docker ps 2>/dev/null | wc -l)
        CONTAINERS=$((CONTAINERS - 1))
        
        echo "  Версия: $DOCKER_VER"
        echo "  Контейнеров: $CONTAINERS"
        
        echo "- **Версия**: $DOCKER_VER" >> "$REPORT"
        echo "- **Контейнеров**: $CONTAINERS" >> "$REPORT"
        
        echo "" >> "$REPORT"
        echo "### Запущенные контейнеры" >> "$REPORT"
        echo "" >> "$REPORT"
        echo '```' >> "$REPORT"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" 2>/dev/null >> "$REPORT"
        echo '```' >> "$REPORT"
    else
        echo "  ⚠️  Docker недоступен из WSL"
        echo "- ⚠️ Docker недоступен из WSL" >> "$REPORT"
    fi
else
    echo "  ⚠️  Docker не установлен в WSL"
    echo "- ⚠️ Docker не установлен в WSL" >> "$REPORT"
fi

echo "" >> "$REPORT"

# Python
echo -e "\n${CYAN}🐍 Python${NC}"
echo "## 🐍 Python" >> "$REPORT"
echo "" >> "$REPORT"

if command -v python3 &> /dev/null; then
    PYTHON_VER=$(python3 --version)
    PIP_VER=$(pip3 --version 2>/dev/null | cut -d' ' -f2)
    
    echo "  Python: $PYTHON_VER"
    echo "  pip: $PIP_VER"
    
    echo "- **Python**: $PYTHON_VER" >> "$REPORT"
    echo "- **pip**: $PIP_VER" >> "$REPORT"
fi

echo "" >> "$REPORT"

# Сетевые интерфейсы
echo -e "\n${CYAN}🌐 Сеть${NC}"
echo "## 🌐 Сеть" >> "$REPORT"
echo "" >> "$REPORT"

ip addr show | grep -E "^[0-9]+:|inet " | while read line; do
    if [[ $line =~ ^[0-9]+: ]]; then
        IFACE=$(echo "$line" | awk '{print $2}' | tr -d ':')
        echo "### $IFACE" >> "$REPORT"
    elif [[ $line =~ inet ]]; then
        IP=$(echo "$line" | awk '{print $2}')
        echo "- IP: $IP" >> "$REPORT"
    fi
done

# Завершение отчёта
cat >> "$REPORT" << 'EOF'

---

## 📊 Преимущества WSL для AI системы

- ✅ Нативная Linux среда на Windows
- ✅ Доступ к Windows файловой системе через /mnt
- ✅ Возможность запуска Linux Docker контейнеров
- ✅ Полная совместимость с Linux инструментами
- ✅ Интеграция с Windows Docker Desktop

---

## 🚀 Использование

Запуск AI системы через WSL:
```bash
# Перейти в директорию проекта
cd /mnt/c/Users/Jack/source/kiro-ai-local

# Запустить Docker Compose
docker-compose up -d

# Проверить статус
curl http://localhost:9000/api/status
```

---

*Отчёт создан автоматически через WSL (Ubuntu)*
EOF

echo -e "\n${GREEN}✅ Отчёт создан: $REPORT${NC}"
echo -e "${CYAN}📄 Просмотр: cat $REPORT${NC}\n"

# Показать краткую сводку
echo -e "${YELLOW}📋 Краткая сводка:${NC}"
echo "  WSL: $WSL_VERSION"
echo "  Дистрибутив: $DISTRO"
echo "  CPU: $CPU_MODEL ($CPU_CORES ядер)"
echo "  RAM: $TOTAL_MEM (используется $USED_MEM)"
echo "  Python: $PYTHON_VER"

echo ""
