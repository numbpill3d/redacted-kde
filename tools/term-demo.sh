#!/usr/bin/env bash
# Terminal content for screenshots: a listing, a log and the 16-colour palette.
cd ~/redacted
p() { printf '\e[90m█\e[0m \e[1mredacted\e[0m ~ %s\n' "$1"; }
p ls; ls --color=always -F | column -c 100
echo; p "git log --oneline -5"; git log --oneline -5 --color=always
echo; p palette
for i in $(seq 0 7); do printf '\e[48;5;%sm      \e[0m ' "$i"; done; echo
for i in $(seq 8 15); do printf '\e[48;5;%sm      \e[0m ' "$i"; done; echo
for i in $(seq 1 7); do printf '\e[3%sm ██████ \e[0m' "$i"; done; echo
echo; printf '\e[90m█\e[0m \e[1mredacted\e[0m ~ cat subject.txt\nname: \e[40m\e[30m█████████\e[0m   seen: \e[40m\e[30m████\e[0m   memory: [withheld]\n'
printf '\n\e[90m█\e[0m \e[1mredacted\e[0m ~ '
