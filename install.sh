#!/bin/bash

M='\033[0;31m'
H='\033[0;32m'
K='\033[1;33m'
B='\033[0;36m'
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

if ada python3; then
    echo -e "  ${H}ok${N}  Python3"
else
    echo -e "  ${M}no${N}  Python3"
    echo ""
    echo -e "  ${B}→${N} install python..."
    pkg install python -y
    if ! ada python3; then
        echo -e "  ${M}gagal install python${N}"
        exit 1
    fi
    echo -e "  ${H}✓${N} Python3 terpasang"
fi

echo ""

URL="https://raw.githubusercontent.com/revanstore235/bussid/main/script.py"

loading "download script.py"
curl -fsSL "$URL" -o script.py

if [ ! -f "script.py" ]; then
    echo ""
    echo -e "  ${M}gagal download script.py${N}"
    exit 1
fi

echo ""

loading "install requests"
pip3 install requests

echo ""
echo -e "  ${H}✓ siap${N}"
echo ""

sleep 2
clear

python script.py