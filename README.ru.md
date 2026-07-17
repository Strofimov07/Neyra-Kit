# neyra-dev-kit

**Русский** · [English](README.md)

Портативный кит дисциплины для AI-агентов (Claude Code, Cursor, Codex).
Ставится в любой git-репозиторий (или обычный workspace через
`--allow-non-git`) и приносит набор **skills** (письменные процедуры — как
правильно делать конкретный класс задач) и **subagents** (специалисты,
которые сами включаются в нужный момент и применяют эти процедуры) — так
агент в твоём репо каждый раз следует одной и той же дисциплине, а не
изобретает процесс заново.

Кит generic по построению: **правило скоупа** — skill описывает *как*,
`settings/` твоего репозитория описывает *что у тебя* (локали, конвенция
API-контрактов, Linear workspace, источники метрик, прод-факты). Ничего
продукто- или компанийно-специфичного в слоях skills нет — это проверяется
линтером (`lint-scope.py`) при каждом изменении кита.

> Этот репозиторий — канонический источник авторинга и релизов общих Neyra
> kits. Продуктовые репозитории являются consumers: установленные в них пути
> кита генерируются и не используются для авторинга общих изменений.

## Авторинг и source policy

Общие skills, agents, hooks, installer, governance, `VERSION`, решения и
evolution signals меняются здесь через reviewable PR. Перед изменением общего
пути запусти:

```bash
python3 agents/neyra-dev-kit/source-policy.py --require-canonical
```

Проверка требует одновременно root-маркер `.neyra-kit-canonical` и
канонический GitHub origin. Consumer-установка получает вместо него
`.neyra-dev-kit.source`. Проблема, найденная в consumer, маршрутизируется сюда
через Kit Evolution; установленная копия не становится конкурирующим source.

## Что внутри

- **26 инженерных skills** (`agents/dev-skills/`) — полный цикл: сбор
  требований (spec-elicitation, EARS) → планы → test-first → систематический
  дебаг → код-ревью → контрактная безопасность → локализация → готовность к
  релизу → регрессии → инциденты → оркестрация нескольких агентов
  (parallel lanes, subagent dispatch, goal mode) → эволюция самого кита.
- **9 продуктовых/growth профилей** (`agents/product-skills/`) — discovery,
  research & insights, дизайн решения, delivery planning, growth-аналитика,
  финансы/бизнес-эффект, finance intelligence, база знаний, delivery-база.
- **5 менеджерских skills** (`agents/mgmt-skills/`) — для руководителей:
  общий каркас отчёта (status-report-shape: RAG + метрики + владельцы гипотез
  + self-eval прошлых гипотез; без индивидуальных рейтингов), хелс-чек
  команды (DORA/SPACE-lite/squad-health/стоимость/надёжность), аудит поставки
  (investment distribution, honesty-check диффа против тикета, bottleneck по
  стадиям), портфельный PMO (граф зависимостей, RAID-реестр с дедупом,
  батч-планирование с гейтом), цели/OKR (фальсифицируемые KR, run-rate,
  челлендж-протокол в обе стороны, приватный personal-режим).
- **Subagents** (`.claude/agents/`) — авто-вызываемые обёртки Claude Code
  вокруг skills, с минимальными наборами инструментов.
- **Инсталлятор** (`agents/neyra-dev-kit/install.sh`) — копирует выбранный
  кит в целевой репозиторий; три subagent'а (`linear-router`,
  `localization-checker`, `contract-checker`) рендерятся из твоего конфига.
  Идемпотентен — перезапускай для апдейта кита.
- **Хуки для трёх поверхностей** (`agents/neyra-dev-kit/hooks/`) — единая
  логика SessionStart/PreToolUse/PostToolUse/Stop для Claude Code, Cursor,
  Codex.
- **Слой knowledge-graph** (`agents/neyra-dev-kit/knowledge/`) — чтобы
  канонические доки не расходились с кодом.

## Четыре кита, один инсталлятор

`install.sh <kit> <repo> <config>` — `kit` выбирает набор (по умолчанию `dev`):

| Кит | Skills | Для кого |
|---|---|---|
| **dev** | всё из `agents/dev-skills/` | инженеры, любой репозиторий |
| **product** | 5 профилей из `agents/product-skills/` | PM / discovery-работа |
| **growth** | 2 профиля из `agents/product-skills/` | growth-работа |
| **mgmt** | всё из `agents/mgmt-skills/` | руководители: приоритеты, цели, эффективность, портфель (`--allow-non-git` — можно в блокнот-workspace) |

Примеры конфигов: `agents/neyra-dev-kit/configs/_*.example.sh`.

## settings/ — твой проектный скоуп

После установки заведи в своём репозитории `settings/` (шаблон — в
[settings/README.md](settings/README.md) этого репо): конфиг установки,
`CONNECTORS.md` (источники метрик для mgmt-кита, лестница paste/CSV → file →
MCP), `facts/` (прод-сигнатуры для incident-runbook), `brand.md`. Для
personal-режима goal-okr — `settings/private/` (обязательно в .gitignore).

## Быстрый старт

```bash
git clone git@github.com:Strofimov07/Neyra-Kit.git
cd Neyra-Kit/agents/neyra-dev-kit
cp configs/_product.example.sh configs/my-repo.sh   # заполни поля
./install.sh dev /path/to/your-repo configs/my-repo.sh
./install.sh --dry-run ...   # посмотреть без записи; --doctor — статус
```

## Подключение MCP-инструментов (Linear / Notion)

Часть subagents ссылается на MCP-инструменты через плейсхолдеры
`{{LINEAR_MCP_PREFIX}}` / `{{NOTION_MCP_PREFIX}}` — id MCP-серверов персональны
(у каждого пользователя свои). Укажи свои в конфиге установки
(`LINEAR_MCP_PREFIX=...`, `NOTION_MCP_PREFIX=...` — найти можно в Claude Code
через `/mcp`), и `install.sh` подставит их при установке. Пустое значение —
соответствующие инструменты у subagent'а просто не активны, всё остальное
работает.
