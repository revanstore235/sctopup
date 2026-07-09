#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
WHITE='\033[1;97m'
NC='\033[0m'

loading() {
    local message=$1
    local percent=0
    
    while [ $percent -le 100 ]; do
        printf "\r  ${CYAN}[${NC} ${WHITE}%s${NC} ${CYAN}]${NC} ${GREEN}%d%%${NC}" "$message" "$percent"
        sleep 0.03
        ((percent+=2))
    done
    printf "\r  ${GREEN}[✓] %s - 100%%${NC}\n" "$message"
}

check_command() {
    command -v "$1" >/dev/null 2>&1
}

clear
echo -e "\n"
echo -e "${YELLOW}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║${NC}                                                  ${YELLOW}║${NC}"
echo -e "${YELLOW}║${NC}        ${WHITE}SCRIPT TOP UP BUSSID${NC}                      ${YELLOW}║${NC}"
echo -e "${YELLOW}║${NC}        ${RED}v2.0${NC}                                        ${YELLOW}║${NC}"
echo -e "${YELLOW}║${NC}                                                  ${YELLOW}║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════╝${NC}\n"

sleep 1

DEPENDENCIES=(
    "python3:Python 3"
    "pip3:PIP 3"
    "git:Git"
)

MISSING=()

echo -e "${PURPLE}  ▶ Mengecek dependencies...${NC}\n"

for dep in "${DEPENDENCIES[@]}"; do
    CMD="${dep%%:*}"
    NAME="${dep##*:}"
    
    if check_command "$CMD"; then
        echo -e "  ${GREEN}✓${NC} $NAME ${GREEN}tersedia${NC}"
    else
        echo -e "  ${RED}✗${NC} $NAME ${RED}tidak ditemukan${NC}"
        MISSING+=("$CMD:$NAME")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}  ⚠ Menginstall ${#MISSING[@]} dependencies...${NC}\n"
    
    for miss in "${MISSING[@]}"; do
        CMD="${miss%%:*}"
        NAME="${miss##*:}"
        
        case $CMD in
            "python3")
                pkg install python -y >/dev/null 2>&1 &
                loading "Install Python 3"
                ;;
            "pip3")
                pkg install python-pip -y >/dev/null 2>&1 &
                loading "Install PIP 3"
                ;;
            "git")
                pkg install git -y >/dev/null 2>&1 &
                loading "Install Git"
                ;;
        esac
    done
    
    echo -e "\n${GREEN}  ✓ Dependencies terinstall${NC}\n"
else
    echo -e "\n${GREEN}  ✓ Semua dependencies tersedia${NC}\n"
fi

echo -e "${PURPLE}  ▶ Download script...${NC}\n"

GITHUB_RAW="https://raw.githubusercontent.com/revanstore235/bussid/main/script.py"

curl -fsSL "$GITHUB_RAW" -o script.py >/dev/null 2>&1 &
loading "Download script.py"

if [ ! -f "script.py" ]; then
    echo -e "\n${RED}  ✗ Gagal download script!${NC}"
    exit 1
fi

echo -e "\n${PURPLE}  ▶ Install module...${NC}\n"

pip3 install requests >/dev/null 2>&1 &
loading "Install requests"

echo -e "\n"
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                                                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}         ${WHITE}✓ INSTALL BERHASIL${NC}                         ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}         ${YELLOW}Script siap dijalankan...${NC}                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                  ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}\n"

sleep 2
clear

python3 script.py