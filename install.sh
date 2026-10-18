#!/bin/bash

M='\033[0;31m'
H='\033[0;32m'
K='\033[1;33m'
B='\033[0;36m'
U='\033[0;35m'
P='\033[1;97m'
N='\033[0m'

loading() {
    local msg="$1"
    local p=0
    while [ $p -le 100 ]; do
        printf "\r  ${B}→${N} ${msg} ${K}%d%%${N}" "$p"
        sleep 0.03
        ((p+=3))
    done
    printf "\r  ${H}✓${N} ${msg}     \n"
}

ada() {
    command -v "$1" >/dev/null 2>&1
}

clear
echo ""
echo -e "  ${P}SC TOP UP BUSSID${N} ${M}v1.0${N}"
echo ""

sleep 1

DEPS=(
    "python3:Python3"
    "pip3:PIP3"
    "git:Git"
)

KURANG=()

for d in "${DEPS[@]}"; do
    C="${d%%:*}"
    NM="${d##*:}"
    if ada "$C"; then
        echo -e "  ${H}ok${N}  $NM"
    else
        echo -e "  ${M}no${N}  $NM"
        KURANG+=("$C:$NM")
    fi
done

if [ ${#KURANG[@]} -gt 0 ]; then
    echo ""
    for x in "${KURANG[@]}"; do
        C="${x%%:*}"
        case $C in
            "python3")
                pkg install python -y >/dev/null 2>&1 &
                loading "Python3"
                ;;
            "pip3")
                pkg install python-pip -y >/dev/null 2>&1 &
                loading "PIP3"
                ;;
            "git")
                pkg install git -y >/dev/null 2>&1 &
                loading "Git"
                ;;
        esac
    done
fi

echo ""

URL="https://raw.githubusercontent.com/revanstore235/bussid/main/script.py"

curl -fsSL "$URL" -o script.py >/dev/null 2>&1 &
loading "script.py"

if [ ! -f "script.py" ]; then
    echo ""
    echo -e "  ${M}gagal${N}"
    exit 1
fi

echo ""

pip3 install requests >/dev/null 2>&1 &
loading "requests"

echo ""
echo -e "  ${H}✓ siap${N}"
echo ""

sleep 2
clear

python script.py