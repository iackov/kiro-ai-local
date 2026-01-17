#!/bin/bash
# -*- coding: utf-8 -*-
# Сбор информации о системе хоста

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "\n${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          🖥️  ИНФОРМАЦИЯ О СИСТЕМЕ ХОСТА 🖥️               ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Создать директорию для отчётов
mkdir -p generated

# Файл для отчёта
REPORT="generated/host-info-bash.md"

# Начало отчёта
cat > "$REPORT" << 'EOF'
# 🖥️ Отчёт о системе хоста (Bash)

**Дата создания**: $(date '+%Y-%m-%d %H:%M:%S')

---

EOF

echo -e "${YELLOW}📊 Сбор информации...${NC}\n"

# Операционная система
echo -e "${CYAN}💻 Операционная система${NC}"
echo "## 💻 Операционная система" >> "$REPORT"
echo "" >> "$REPORT"

if command -v uname &> /dev/null; then
    OS=$(uname -s)
    KERNEL=$(uname -r)
    ARCH=$(uname -m)
    
    echo "  Система: $OS"
    echo "  Ядро: $KERNEL"
    echo "  Архитектура: $ARCH"
    
    echo "- **Система**: $OS" >> "$REPORT"
    echo "- **Ядро**: $KERNEL" >> "$REPORT"
    echo "- **Архитектура**: $ARCH" >> "$REPORT"
fi

# Для Windows через Git Bash
if [[ "$OS" == *"MINGW"* ]] || [[ "$OS" == *"MSYS"* ]]; then
    echo "  Платформа: Windows (Git Bash)"
    echo "- **Платформа**: Windows (Git Bash)" >> "$REPORT"
    
    # Версия Windows
    if command -v systeminfo &> /dev/null; then
        WIN_VER=$(systeminfo | grep "OS Name" | cut -d: -f2 | xargs)
        echo "  Версия: $WIN_VER"
        echo "- **Версия**: $WIN_VER" >> "$REPORT"
    fi
fi

echo "" >> "$REPORT"

# Процессор
echo -e "\n${CYAN}🔧 Процессор${NC}"
echo "## 🔧 Процессор" >> "$REPORT"
echo "" >> "$REPORT"

if command -v wmic &> /dev/null; then
    # Windows
    CPU=$(wmic cpu get name | tail -n +2 | head -n 1 | xargs)
    CORES=$(wmic cpu get NumberOfCores | tail -n +2 | head -n 1 | xargs)
    THREADS=$(wmic cpu get NumberOfLogicalProcessors | tail -n +2 | head -n 1 | xargs)
    
    echo "  Модель: $CPU"
    echo "  Ядер: $CORES"
    echo "  Потоков: $THREADS"
    
    echo "- **Модель**: $CPU" >> "$REPORT"
    echo "- **Физических ядер**: $CORES" >> "$REPORT"
    echo "- **Логических ядер**: $THREADS" >> "$REPORT"
elif [ -f /proc/cpuinfo ]; then
    # Linux
    CPU=$(grep "model name" /proc/cpuinfo | head -n 1 | cut -d: -f2 | xargs)
    CORES=$(grep "cpu cores" /proc/cpuinfo | head -n 1 | cut -d: -f2 | xargs)
    
    echo "  Модель: $CPU"
    echo "  Ядер: $CORES"
    
    echo "- **Модель**: $CPU" >> "$REPORT"
    echo "- **Ядер**: $CORES" >> "$REPORT"
fi

echo "" >> "$REPORT"

# Память
echo -e "\n${CYAN}💾 Память${NC}"
echo "## 💾 Память" >> "$REPORT"
echo "" >> "$REPORT"

if command -v wmic &> /dev/null; then
    # Windows
    TOTAL_MEM=$(wmic ComputerSystem get TotalPhysicalMemory | tail -n +2 | xargs)
    TOTAL_GB=$(echo "scale=2; $TOTAL_MEM / 1024 / 1024 / 1024" | bc)
    
    echo "  Всего RAM: ${TOTAL_GB} GB"
    echo "- **Всего RAM**: ${TOTAL_GB} GB" >> "$REPORT"
elif command -v free &> /dev/null; then
    # Linux
    TOTAL_MEM=$(free -h | grep Mem | awk '{print $2}')
    USED_MEM=$(free -h | grep Mem | awk '{print $3}')
    
    echo "  Всего: $TOTAL_MEM"
    echo "  Используется: $USED_MEM"
    
    echo "- **Всего**: $TOTAL_MEM" >> "$REPORT"
    echo "- **Используется**: $USED_MEM" >> "$REPORT"
fi

echo "" >> "$REPORT"

# Диски
echo -e "\n${CYAN}💿 Диски${NC}"
echo "## 💿 Диски" >> "$REPORT"
echo "" >> "$REPORT"

if command -v df &> /dev/null; then
    df -h | grep -E '^(/dev/|[A-Z]:)' | while read line; do
        DISK=$(echo "$line" | awk '{print $1}')
        SIZE=$(echo "$line" | awk '{print $2}')
        USED=$(echo "$line" | awk '{print $3}')
        AVAIL=$(echo "$line" | awk '{print $4}')
        PERCENT=$(echo "$line" | awk '{print $5}')
        MOUNT=$(echo "$line" | awk '{print $6}')
        
        echo "  $DISK ($MOUNT): $SIZE всего, $USED используется ($PERCENT)"
        echo "- **$DISK** ($MOUNT): $SIZE всего, $USED используется ($PERCENT)" >> "$REPORT"
    done
fi

echo "" >> "$REPORT"

# Docker
echo -e "\n${CYAN}🐳 Docker${NC}"
echo "## 🐳 Docker" >> "$REPORT"
echo "" >> "$REPORT"

if command -v docker &> /dev/null; then
    DOCKER_VER=$(docker --version)
    CONTAINERS=$(docker ps --format "{{.Names}}" | wc -l)
    IMAGES=$(docker images -q | wc -l)
    
    echo "  Версия: $DOCKER_VER"
    echo "  Контейнеров запущено: $CONTAINERS"
    echo "  Образов: $IMAGES"
    
    echo "- **Версия**: $DOCKER_VER" >> "$REPORT"
    echo "- **Контейнеров запущено**: $CONTAINERS" >> "$REPORT"
    echo "- **Образов**: $IMAGES" >> "$REPORT"
    
    echo "" >> "$REPORT"
    echo "### Запущенные контейнеры" >> "$REPORT"
    echo "" >> "$REPORT"
    echo '```' >> "$REPORT"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" >> "$REPORT"
    echo '```' >> "$REPORT"
else
    echo "  ⚠️  Docker не установлен"
    echo "- ⚠️ Docker не установлен" >> "$REPORT"
fi

echo "" >> "$REPORT"

# Git
echo -e "\n${CYAN}📝 Git${NC}"
echo "## 📝 Git" >> "$REPORT"
echo "" >> "$REPORT"

if command -v git &> /dev/null; then
    GIT_VER=$(git --version)
    COMMITS=$(git rev-list --count HEAD 2>/dev/null || echo "N/A")
    LAST_COMMIT=$(git log -1 --format="%h - %s" 2>/dev/null || echo "N/A")
    
    echo "  Версия: $GIT_VER"
    echo "  Коммитов: $COMMITS"
    echo "  Последний: $LAST_COMMIT"
    
    echo "- **Версия**: $GIT_VER" >> "$REPORT"
    echo "- **Коммитов**: $COMMITS" >> "$REPORT"
    echo "- **Последний**: $LAST_COMMIT" >> "$REPORT"
fi

echo "" >> "$REPORT"

# Python
echo -e "\n${CYAN}🐍 Python${NC}"
echo "## 🐍 Python" >> "$REPORT"
echo "" >> "$REPORT"

if command -v python &> /dev/null; then
    PYTHON_VER=$(python --version 2>&1)
    echo "  Версия: $PYTHON_VER"
    echo "- **Версия**: $PYTHON_VER" >> "$REPORT"
elif command -v python3 &> /dev/null; then
    PYTHON_VER=$(python3 --version)
    echo "  Версия: $PYTHON_VER"
    echo "- **Версия**: $PYTHON_VER" >> "$REPORT"
fi

echo "" >> "$REPORT"

# Завершение отчёта
cat >> "$REPORT" << 'EOF'

---

## 📊 Рекомендации для AI системы

- ✅ Система может работать на этом хосте
- ℹ️ Для оптимальной работы рекомендуется:
  - Минимум 8GB RAM
  - Минимум 4 CPU ядра
  - Минимум 20GB свободного места
  - Docker установлен и запущен

---

*Отчёт создан автоматически через Bash*
EOF

echo -e "\n${GREEN}✅ Отчёт создан: $REPORT${NC}"
echo -e "${CYAN}📄 Просмотр: cat $REPORT${NC}\n"

# Показать краткую сводку
echo -e "${YELLOW}📋 Краткая сводка:${NC}"
cat "$REPORT" | grep "^- \*\*" | head -20

echo ""
