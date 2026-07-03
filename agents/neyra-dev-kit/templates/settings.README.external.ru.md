# settings/ — проектный скоуп (создаёшь у себя)

**Русский** · [English](README.md)

Слои skills кита (`agents/dev-skills/`, `agents/product-skills/`,
`agents/mgmt-skills/`) — **generic-протокол**: фактов твоего проекта в них
нет. Всё специфичное живёт в каталоге `settings/` **твоего репозитория** (не
в этом ките):

| Путь | Что там | Кто использует |
|---|---|---|
| `settings/configs/<repo>.sh` | твой конфиг установки (копия `agents/neyra-dev-kit/configs/_*.example.sh`) | `install.sh` |
| `settings/CONNECTORS.md` | твои источники метрик для mgmt-кита (лестница paste/CSV → file → MCP; копия `CONNECTORS.example.md`) | team-health-check, delivery-audit, portfolio-pmo, goal-okr |
| `settings/facts/` | твои прод-факты (например `incident-runbook.md` — известные сигнатуры сбоев) | incident-runbook |
| `settings/brand.md` | твои правила нейминга/бренда | всё, что пишет пользовательские тексты |
| `settings/private/` | **добавь в .gitignore** — данные personal-режима goal-okr (личные KR, evidence trail, черновики планов). Никогда не коммитится и не шарится | только personal-режим goal-okr |

Правило одной строкой: *будет ли эта строка правдой в чужом репозитории?*
Если да — это протокол, место ему в скилле (issue/PR в кит). Если нет — ей
место здесь.

В самом ките этот каталог несёт только examples — твой настоящий `settings/`
живёт в твоём репозитории.
