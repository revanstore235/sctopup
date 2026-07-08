#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
WHITE='\033[1;97m'
NC='\033[0m'
BOLD='\033[1m'
BLINK='\033[5m'

loading() {
    local message=$1
    local frames=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
    local percent=0
    
    while [ $percent -le 100 ]; do
        local i=$(( percent % 10 ))
        printf "\r  ${CYAN}${frames[$i]}${NC} ${WHITE}%s${NC} ${PURPLE}[${NC}"
        local filled=$(( percent / 2 ))
        local empty=$(( 50 - filled ))
        printf "${GREEN}%${filled}s${NC}" | tr ' ' '█'
        printf "${RED}%${empty}s${NC}" | tr ' ' '░'
        printf "${PURPLE}]${NC} ${YELLOW}%d%%${NC}" "$percent"
        sleep 0.02
        ((percent+=2))
    done
    printf "\r  ${GREEN}✓${NC} ${WHITE}%s${NC} ${PURPLE}[${GREEN}" "$message"
    printf '%50s' | tr ' ' '█'
    printf "${PURPLE}]${NC} ${GREEN}100%% Selesai!${NC}\n"
}

check_command() {
    command -v "$1" >/dev/null 2>&1
}

draw_box() {
    local width=45
    local text="$1"
    local color="$2"
    echo -e "${color}╔$(printf '═%.0s' $(seq 1 $width))╗${NC}"
    echo -e "${color}║${NC} ${BOLD}${WHITE}$(printf "%-${width}s" "$text")${NC} ${color}║${NC}"
    echo -e "${color}╚$(printf '═%.0s' $(seq 1 $width))╝${NC}"
}

clear
echo -e "\n"
echo -e "${PURPLE}   ╔═══════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}   ║${NC}                                           ${PURPLE}║${NC}"
echo -e "${PURPLE}   ║${NC}  ${RED}█▀█${NC} ${RED}█▀▀${NC} ${RED}█░█${NC} ${RED}█▀█${NC} ${RED}█▄░█${NC}  ${WHITE}█▀${NC} ${RED}▀█▀${NC} ${RED}█▀█${NC} ${RED}█▀█${NC} ${RED}█▀▀${NC}  ${PURPLE}║${NC}"
echo -e "${PURPLE}   ║${NC}  ${RED}█▀▄${NC} ${RED}█▀▀${NC} ${RED}▀▄▀${NC} ${RED}█▀█${NC} ${RED}█░▀█${NC}  ${WHITE}▄█${NC} ${RED}░█░${NC} ${RED}█▄█${NC} ${RED}█▀▄${NC} ${RED}██▄${NC}  ${PURPLE}║${NC}"
echo -e "${PURPLE}   ║${NC}                                           ${PURPLE}║${NC}"
echo -e "${PURPLE}   ║${NC}         ${YELLOW}⚡ AUTO INSTALLER v2.0 ⚡${NC}         ${PURPLE}║${NC}"
echo -e "${PURPLE}   ║${NC}                                           ${PURPLE}║${NC}"
echo -e "${PURPLE}   ╚═══════════════════════════════════════════╝${NC}\n"

sleep 1

DEPENDENCIES=(
    "python3:Python 3"
    "pip3:PIP 3"
    "git:Git"
)

MISSING=()

echo -e "${CYAN}  ╭─────────────────────────────────────────╮${NC}"
echo -e "${CYAN}  │${NC}  ${WHITE}🔍 MEMERIKSA DEPENDENCIES${NC}               ${CYAN}│${NC}"
echo -e "${CYAN}  ╰─────────────────────────────────────────╯${NC}\n"

for dep in "${DEPENDENCIES[@]}"; do
    CMD="${dep%%:*}"
    NAME="${dep##*:}"
    
    if check_command "$CMD"; then
        echo -e "  ${GREEN}✓${NC} ${WHITE}$NAME${NC} ${GREEN}sudah terinstall${NC}"
    else
        echo -e "  ${RED}✗${NC} ${WHITE}$NAME${NC} ${RED}belum terinstall${NC}"
        MISSING+=("$CMD:$NAME")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}  ⚠ ${#MISSING[@]} dependency perlu diinstall${NC}\n"
    
    for miss in "${MISSING[@]}"; do
        CMD="${miss%%:*}"
        NAME="${miss##*:}"
        
        echo -e "${CYAN}  [+] Menginstall ${WHITE}$NAME${NC}..."
        
        case $CMD in
            "python3")
                pkg install python -y >/dev/null 2>&1 &
                loading "Python 3"
                ;;
            "pip3")
                pkg install python-pip -y >/dev/null 2>&1 &
                loading "PIP 3"
                ;;
            "git")
                pkg install git -y >/dev/null 2>&1 &
                loading "Git"
                ;;
            *)
                echo -e "  ${RED}✗ Gagal install $NAME${NC}"
                ;;
        esac
    done
    
    echo -e "\n${GREEN}  ✓ Semua dependencies berhasil diinstall!${NC}\n"
else
    echo -e "\n${GREEN}  ✓ Semua dependencies sudah tersedia!${NC}\n"
fi

echo -e "${CYAN}  ╭─────────────────────────────────────────╮${NC}"
echo -e "${CYAN}  │${NC}  ${WHITE}📦 DOWNLOAD SCRIPT${NC}                      ${CYAN}│${NC}"
echo -e "${CYAN}  ╰─────────────────────────────────────────╯${NC}\n"

GITHUB_RAW="https://raw.githubusercontent.com/revanstore235/sctopup/main/script.py"

curl -fsSL "$GITHUB_RAW" -o script.py >/dev/null 2>&1 &
loading "Download script.py"

if [ ! -f "script.py" ]; then
    echo -e "\n${RED}  ✗ Gagal download script.py!${NC}"
    echo -e "${YELLOW}  Cek koneksi internet lo ya...${NC}"
    exit 1
fi

echo -e "\n${CYAN}  [+] Install module Python...${NC}"
pip3 install requests >/dev/null 2>&1 &
loading "Install requests"

echo -e "\n"
echo -e "${GREEN}  ╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}  ║${NC}     ${WHITE}${BOLD}✓ INSTALL BERHASIL!${NC}                       ${GREEN}║${NC}"
echo -e "${GREEN}  ║${NC}     ${YELLOW}Script siap dijalankan...${NC}                ${GREEN}║${NC}"
echo -e "${GREEN}  ╚═══════════════════════════════════════════╝${NC}\n"

sleep 2
clear

python3 script.py