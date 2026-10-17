<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/header-dark.svg">
  <img src="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/header-light.svg" alt="antharmaya labs — agent and systems infrastructure" width="100%">
</picture>

[antharmaya.com](https://antharmaya.com) · [deedroll](https://deedroll.antharmaya.com) · [tools](https://antharmaya.com/tools)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/s-about-dark.svg">
  <img src="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/s-about-light.svg" alt="about" width="100%">
</picture>

> AI agents can run your systems now. Almost nothing tells them where to stop.

An independent studio in India building the layer underneath: what an agent may
spend, what it remembers, how it decides, what it may touch, and the
kernel-level observability that says what actually happened.

Everything is open source (MIT, or MIT/Apache-2.0) and installs without root.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/s-projects-dark.svg">
  <img src="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/s-projects-light.svg" alt="projects" width="100%">
</picture>

What each tool covers, and how it installs today.

[**deedroll**](https://github.com/antharmaya/deedroll) · what it may run
Reads what an MCP server's code actually does, compares it with what its
listing declares, and cites the file and line for each difference. Never runs
what it reads.
Browser: [deedroll.antharmaya.com](https://deedroll.antharmaya.com) ·
CLI (Node 22+, no dependencies): `git clone https://github.com/antharmaya/deedroll && node deedroll/bin/deedroll.js --installed`

[**rateguard**](https://github.com/varbees/rateguard) · what it may spend
Token budgets, loop detection and circuit breakers, in-process. Three SDKs held
to one conformance suite.
`npm install @varbees/rateguard-node` · `pip install varbees-rateguard` ·
`go get github.com/varbees/rateguard/packages/sdk-go`

[**token cost**](https://github.com/antharmaya/tokencost) · what a run will cost
Prices a whole agent run: context regrowth, prompt caching, long-context rates,
tool and thinking tokens. `npm i @antharmaya/tokencost` ·
[in the browser](https://antharmaya.com/tools/token-cost)

[**memory bridge**](https://github.com/antharmaya/mem-bridge) · what it remembers
One local, searchable memory across every coding agent's conversations on the
machine, for Hermes Agent and MCP.
`curl -fsSL https://antharmaya.com/memory-bridge/install.sh | bash`

[**council of hats**](https://github.com/antharmaya/council-of-hats) · how it decides
Deterministic multi-perspective review with no LLM in the decision path, so it
cannot drift.
`curl -fsSL https://raw.githubusercontent.com/antharmaya/council-of-hats/v0.2.1/install.sh | bash`

[**agent-linux-control**](https://github.com/antharmaya/agent-linux-control) · what it may touch
Native OS inspection through D-Bus, portals and accessibility trees before
falling back to synthetic input. No sudo unless asked for (`--with-system`).
`curl -fsSL https://raw.githubusercontent.com/antharmaya/agent-linux-control/v0.6.0/install.sh | sh`

[**systems-forge**](https://github.com/antharmaya/sys-forge) · whether its code survives
Tested breakers, retries, an MCP server, and a cross-agent `AGENTS.md`
contract, as a Claude Code skill.
`curl -fsSL https://raw.githubusercontent.com/antharmaya/sys-forge/v0.2.3/install.sh | bash`

[**siphon**](https://github.com/antharmaya/siphon) · one sink for downloads
Video from 1,700+ sites, image posts and `blob:` video, from a CLI, a browser
button or a queue.
`curl -fsSL https://raw.githubusercontent.com/antharmaya/siphon/master/install.sh | sh`

[**stallwatch**](https://github.com/varbees/stallwatch) · the machine underneath · archived
Names the systemd unit, then the process, that stalled the machine. Finished at
v0.2.2 and archived on 2026-10-01. `cargo install stallwatch`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/s-stats-dark.svg">
  <img src="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/s-stats-light.svg" alt="stats" width="100%">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/stats-dark.svg">
  <img src="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/stats-light.svg" alt="languages by bytes written, and the year" width="100%">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/calendar-dark.svg">
  <img src="https://raw.githubusercontent.com/antharmaya/.github/main/profile/assets/calendar-light.svg" alt="a year of daily contributions" width="100%">
</picture>
