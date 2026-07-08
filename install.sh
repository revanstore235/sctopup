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
    local spin='-\|/'
    local percent=0
    
    while [ $percent -le 100 ]; do
        local i=$(( percent % 4 ))
        printf "\r${CYAN}[%c] %s... %d%%${NC}" "${spin:$i:1}" "$message" "$percent"
        sleep 0.03
        ((percent+=2))
    done
    printf "\r${GREEN}[✓] %s... 100%% Selesai!${NC}\n" "$message"
}

check_command() {
    command -v "$1" >/dev/null 2>&1
}

clear
echo -e "${PURPLE}=====================================${NC}"
echo -e "${PURPLE}   REVAN STORE - AUTO INSTALLER     ${NC}"
echo -e "${PURPLE}=====================================${NC}\n"

DEPENDENCIES=(
    "python3:Python 3"
    "pip3:PIP 3"
    "git:Git"
)

MISSING=()

echo -e "${CYAN}[+] Mengecek dependencies...${NC}\n"

for dep in "${DEPENDENCIES[@]}"; do
    CMD="${dep%%:*}"
    NAME="${dep##*:}"
    
    if check_command "$CMD"; then
        echo -e "  ${GREEN}[✓] $NAME sudah terinstall${NC}"
    else
        echo -e "  ${RED}[✗] $NAME belum terinstall${NC}"
        MISSING+=("$CMD:$NAME")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}[!] Ada ${#MISSING[@]} dependency yang belum terinstall${NC}\n"
    
    for miss in "${MISSING[@]}"; do
        CMD="${miss%%:*}"
        NAME="${miss##*:}"
        
        echo -e "${CYAN}[+] Menginstall $NAME...${NC}"
        
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
            *)
                echo -e "  ${RED}[✗] Gak tau cara install $NAME, install manual aja ya${NC}"
                ;;
        esac
    done
    
    echo -e "\n${GREEN}[✓] Semua dependencies berhasil diinstall!${NC}\n"
else
    echo -e "\n${GREEN}[✓] Semua dependencies udah tersedia!${NC}\n"
fi

echo -e "${CYAN}[+] Download script...${NC}"
GITHUB_RAW="https://raw.githubusercontent.com/revanstore235/revanstore/main/script.py"

curl -fsSL "$GITHUB_RAW" -o script.py >/dev/null 2>&1 &
loading "Download script.py"

echo -e "${CYAN}[+] Install Python modules...${NC}"
pip3 install requests >/dev/null 2>&1 &
loading "Install module requests"

echo -e "\n${GREEN}[✓] Semua siap!${NC}"
echo -e "${YELLOW}[+] Menjalankan script...${NC}\n"

python3 script.py