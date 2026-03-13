---
title: "I Built This"
date: 2026-03-13
author: kdairatchi
tags: [personal, launch, story]
summary: "Not a press release. Just me explaining what I actually built, why I built it, and what I want it to become."
---

# I Built This

I'm not going to write a press release.

I'm going to tell you what actually happened.

---

## Where it started

I had multiple Claude terminals open. Three of them, all working on the same project. One doing backend, one doing frontend, one writing tests.

They kept stepping on each other.

Editing the same file at the same time. Making conflicting decisions. One would refactor something the other had just built. No awareness of each other at all.

I thought: this is the dumbest unsolved problem. Three agents, one codebase, no coordination. There had to be a way to fix it.

So I built the War Room.

A shared mission board. File locks. A way for agents to claim tasks, share what they found, and stay out of each other's way. I built it for myself, on my own machine, on WSL2. It worked. Then I kept going.

---

## What I actually built

ProwlrBot started as a coordination layer for multi-agent development. Then it became more.

I added channels — Discord, Telegram, DingTalk, Feishu, iMessage. The same agent, everywhere you already are. Not a new app. Not a new interface. Just your existing channels, now powered by an agent that actually acts instead of just chatting.

I added monitoring. Give it a list of URLs and tell it what you care about. It checks them on a schedule. It tells you when something changes. Not a notification you have to manually set up — an agent that actually reads the page and decides if it matters.

I added skills. PDF processing. Spreadsheets. Browser automation. News. Email. Things the agent knows how to do, that you can install like packages.

I added the ROAR Protocol alongside it — a communication standard for agents to talk to each other. Typed messages, signed identities, capability delegation. The kind of infrastructure that doesn't exist yet because everyone's building on top of OpenAI and hoping the platform stays stable.

I did all of this without spending a dollar on hosted tools. It runs on my machine. It uses my API keys. It doesn't phone home.

---

## Why I'm putting it out there

Because I use it every day and I think other people should too.

Not because it's perfect. It's not. There are rough edges. The Docker image probably needs work. The Windows install path has quirks. Some channels are easier to set up than others.

But the core of it — the monitoring, the automation, the multi-agent coordination, the skill system — that works. I've been running it on my homelab for months.

I built this with AI assistance. I'm not hiding that. Claude helped me write code, structure ideas, catch bugs I missed. But the decisions — what to build, why it should exist, how it should work, what it should feel like — those are mine. The same way a developer uses a compiler or a designer uses Figma. The tools don't change what you built. They change how fast you built it.

---

## What I want this to become

I want ProwlrBot to be the agent platform for people who don't want to hand their data to someone else.

For the homelab crowd. For developers who self-host everything. For the people who read r/selfhosted and immediately check if something has a Docker image. For anyone who's been burned by a service going down or changing its pricing or selling their data.

I want a community around it. People building skills and sharing them. People running it on their Raspberry Pi and their cloud VMs and their gaming rig. People telling me what's broken and what they wish it could do.

If you use it and something's wrong, open an issue. If you have an idea, start a discussion. If you build a skill that other people would want, share it.

This is just the start.

— kdairatchi

---

*ProwlrBot is free and open source. Self-host it from [GitHub](https://github.com/ProwlrBot/prowlrbot). If it saves you time and you want to say thanks, there's a [sponsor link](https://github.com/sponsors/kdairatchi) — but that's completely optional. The software is yours either way.*
