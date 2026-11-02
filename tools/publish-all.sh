#!/usr/bin/env bash
# Publish the whole Redacted suite: 14 piece repos (repos/redacted-*) and the hub (this tree).
# Each gets description, topics (max 20) and a v1.0 release carrying its KDE Store tarball.
# Safe to re-run: existing repos/tags/releases are reused, new commits are pushed.
set -euo pipefail
B=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
K=$HOME/Documents/"Redacted Release"
O=numbpill3d
CO="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

publish() {  # dir repo description tarball tags...
    local dir=$1 repo=$2 desc=$3 tar=$4; shift 4
    cd "$dir"
    [[ -d .git ]] || git init -q -b main
    git add -A
    git diff --cached --quiet || git commit -q -m "${repo}: Redacted v1.0

$CO"
    git rev-parse -q --verify refs/tags/v1.0 >/dev/null || git tag -a v1.0 -m "$repo v1.0"
    gh repo view "$O/$repo" >/dev/null 2>&1 || gh repo create "$O/$repo" --public --description "$desc" >/dev/null
    git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$O/$repo.git"
    git push -q -u origin main
    git push -q origin v1.0
    local a=(); for t in "$@"; do a+=(--add-topic "$t"); done
    gh repo edit "$O/$repo" --description "$desc" "${a[@]}" >/dev/null
    if ! gh release view v1.0 -R "$O/$repo" >/dev/null 2>&1; then
        if [[ -n $tar ]]; then gh release create v1.0 "$tar" -R "$O/$repo" --title "$repo v1.0" --notes "$desc" >/dev/null
        else gh release create v1.0 -R "$O/$repo" --title "$repo v1.0" --notes "$desc" >/dev/null; fi
    elif [[ -n $tar ]]; then
        gh release upload v1.0 "$tar" -R "$O/$repo" --clobber >/dev/null
    fi
    echo "ok  https://github.com/$O/$repo"
}

for d in "$B"/repos/redacted-*; do
    r=$(basename "$d")
    L="$K/$r/STORE-LISTING.txt"
    desc=$(awk '/^SUMMARY:/{getline; print; exit}' "$L" | cut -c1-340)
    mapfile -t tags < <(sed -n 's/^TAGS: //p' "$L" | tr ',' '\n' | tr -d ' ' | awk 'NF && !seen[$0]++' | head -20)
    publish "$d" "$r" "$desc" "$K/$r/$r.tar.gz" "${tags[@]}"
done

publish "$B" redacted "Redacted: a monochrome-black KDE Plasma 6 suite of obfuscation and censorship. Global theme, Aurorae, Plasma style, Kvantum, icons, SDDM, Plymouth, animated wallpaper, KWin effect + script, clock, all generated from one palette." "" \
    redacted kde plasma6 plasma-6 dark black monochrome grayscale censored glitch static pixel sddm plymouth aurorae kvantum kwin-effect kde-theme theme-suite minimal
