## Commit rules

- **Git User Rotation (Daily Limit):**
  - Check today's commit count untuk ketiga user sebelum commit (`git log --since="midnight" --author="<email>"`).
  - Limit: Diva = 5 commits/day, Robert = 10 commits/day, Queen = 10 commits/day.
  - Prioritas:
    1. Diva today < 5 → pakai Diva (`./git-switch.sh diva`, push ke `origin-diva`)
    2. Diva >= 5 dan Robert < 10 → pakai Robert (`./git-switch.sh robert`, push ke `origin-robert`)
    3. Diva >= 5, Robert >= 10, dan Queen < 10 → pakai Queen (`./git-switch.sh queen`, push ke `origin-queen`)
    4. Ketiganya penuh → fallback ke Diva
- **Jangan commit**: `docs/superpowers/**`, `.superpowers/**`, `konteks/**`, `QA_NOTES.md`, skill locks, agent files, session scratch.
- Commit message harus terdengar manusiawi (short imperative). Jangan ada kata-kata AI/agent/sesi/generate.
- Jangan force-push kecuali user minta eksplisit.
  //
  // CLAUDE.md
  // urbanGrow
  //
  // Created by MacBook on 16/08/26.
  //
