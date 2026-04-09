# Cline User Guide

## Overview

Cline is an AI-powered coding assistant built into Visual Studio Code. It can read and edit files in your workspace, run terminal commands, and call external tools via MCP servers — including the Azure AI Search indexes you set up through the RAG Website. This guide covers both the initial setup a new user needs to complete and the features available for everyday use.

---

## Setup

Complete these steps once before using Cline for the first time.

### Prerequisites

- WireGuard is connected on your local machine

### Step 1: Install Visual Studio Code

1. Go to [https://code.visualstudio.com/](https://code.visualstudio.com/).
2. Download and install the version for your operating system.
3. Launch Visual Studio Code.

### Step 2: Install the Cline Extension

1. Open the **Extensions** view with `Ctrl+Shift+X`.
2. Search for **Cline**.
3. Click **Install**.

### Step 3: Configure the API Connection

**If this is your first time installing Cline**, the setup wizard opens automatically:

1. On the "How will you use Cline?" screen, select **Bring my own API key** and click **Continue**.
2. On the "Configure your provider" screen, set:
    - **API Provider:** `OpenAI Compatible`
    - **Base URL:** `http://10.55.55.1:4000`
    - **OpenAI Compatible API Key:** `none`
    - **Model ID:** `gpt-4o`

    ![Cline API Config](images/Cline%20API%20Config.png)

3. Click **Continue**.

**If Cline is already installed**, open Settings directly:

1. Open the Cline panel from the Activity Bar (left sidebar).
2. Click the **gear icon** in the top-right corner of the Cline panel.
3. Under **API Configuration**, set the same four fields listed above.
4. Click **Done**.

### Step 4: Connect to the MCP Server

1. Click the **MCP Servers icon** (plug icon) in the top-right corner of the Cline panel.
2. Open the **Remote Servers** tab.
3. Add a new server with:
    - **Server Name:** `Azure MCP` (or any label you prefer)
    - **Server URL:** `http://10.55.55.1:8000/mcp`
    - **Transport Type:** `Streamable HTTP`

    ![Cline MCP Config](images/Cline%20MCP%20Config.png)

4. Save the entry.

### Step 5: Verify the Connections

**Model connection:** Open a new Cline chat. The bottom bar of the panel should show the model name (e.g., `openai-compat:gpt-4o`). Send a short message — if Cline responds, the connection is working.

**MCP connection:** Open MCP Servers, go to the **Configure** tab, and confirm your server entry shows a **green dot**, indicating it is connected.

---

## The Cline Interface

### Main Panel

When you open Cline, the panel shows recent conversations at the top and the chat input at the bottom. Type your task in the input field and press **Enter** to send.

The bottom bar of the panel always shows the active model name. The **Plan** and **Act** buttons to the right of it switch between the two operating modes (described below).

### Toolbar Icons (Bottom Left)

The four icons to the left of the chat input provide quick access to common actions:

![Cline Toolbar](images/Cline%20Toolbar%20Snip.png)

| Button | Action |
|---|---|
| **@** | **Add Context** — attach files, folders, URLs, or other references to your message |
| **+** | **Add Files & Images** — opens the file explorer to attach local files or screenshots |
| MCP servers icon | **Manage MCP Servers** — view and configure connected MCP tool servers |
| Rules icon | **Manage Cline Rules & Workflows** — open the panel for Rules, Workflows, Hooks, and Skills |

---

## Adding Context

Cline works best when it knows what you are working on. You can add context in several ways.

### @ Context Picker

Type `@` in the chat input or click the **@** button to open the context picker menu. The following options are available:

![Cline @ list](images/Cline%20at%20list.png)

- **Paste URL to fetch contents** — fetches and attaches the contents of a web page
- **Problems** — attaches the current errors and warnings from the VS Code Problems panel
- **Terminal** — attaches the output from the current terminal session
- **Git Commits** — attaches recent git commit history
- **Add Folder** — browse and attach a folder from your workspace
- **Add File** — browse and attach a specific file

### Files and Images

Click the **+** icon to open the file explorer and attach local files or screenshots directly to your message. This is useful for sharing error screenshots, diagrams, or files outside your current workspace.

### Drag and Drop

Drag a file from the VS Code Explorer directly into the Cline chat input to attach it.

---

## Plan and Act Modes

![Cline Plan/Act Config](images/Cline%20Plan%20and%20Act%20snip.png)

Cline operates in two modes, toggled with the **Plan** and **Act** buttons at the bottom of the panel.

### Plan Mode

In Plan mode, Cline thinks through the task and proposes an approach before doing anything. Use this when:

- The task is complex or has multiple steps
- You want to review the strategy before Cline starts making changes
- You are using a strong reasoning model to design a plan for a cheaper model to execute

Cline will ask clarifying questions and outline what it intends to do. No files are edited and no commands are run until you switch to Act mode.

### Act Mode

In Act mode, Cline executes tasks directly. Each file edit or terminal command is shown as a proposed action that you approve or reject before it runs (unless Auto-approve is enabled for that action type).

Use Act mode once you are satisfied with the plan, or for straightforward tasks that do not need a planning step.

---

## Auto-Approve

The **Auto-approve** section at the bottom of the Cline panel controls which actions Cline can take without prompting you each time. This speeds up your workflow for actions you trust.

![Cline Auto Approve Config](images/Cline%20Auto%20Approve.png)

| Permission | What it allows |
|---|---|
| **Read project files** | Read files inside the current VS Code workspace |
| **Read all files** | Read any file on the machine |
| **Edit project files** | Modify files inside the workspace without asking |
| **Execute safe commands** | Run low-risk terminal commands (e.g., `ls`, `cat`) |
| **Execute all commands** | Run any terminal command without asking |
| **Use the browser** | Open and interact with web pages |
| **Use MCP servers** | Call MCP tools (e.g., RAG index search) without asking |

The default configuration enables **Read project files**, **Execute safe commands**, and **Use MCP servers**. Enable additional permissions only if the interruptions are slowing you down and you trust Cline's judgment for that action type.

!!! warning
    Enabling **Edit project files** or **Execute all commands** means Cline can modify your code and run arbitrary commands without showing you a preview first. Only enable these if you are comfortable with that level of autonomy.

---

## Rules, Workflows, Hooks, and Skills

Click the **Manage Cline Rules & Workflows** icon (bottom left of the chat input) to open the management panel. It has four tabs.

### Rules

Rules provide Cline with persistent system-level guidance that applies to every conversation — without you having to repeat yourself each time. Think of them as standing instructions.

![Cline Rules](images/Cline%20Rules.png)

- **Global Rules** apply across all workspaces on your machine.
- **Workspace Rules** apply only to the current VS Code project.

Examples of useful rules:
- "Always write comments in English."
- "Never modify test files unless I explicitly ask."
- "When working in this repo, follow the coding conventions in `CONTRIBUTING.md`."

Click **+** next to the appropriate section and point it at a rule file (a plain text or markdown file containing your instructions).

### Workflows

Workflows define a reusable series of steps for repetitive tasks. Once defined, you invoke a workflow by typing `/workflow-name` in the chat.

![Cline Workflows](images/Cline%20Workflows.png)

- **Global Workflows** are available in any workspace.
- **Workspace Workflows** are specific to the current project.

Example workflows:
- `/deploy` — run tests, build, and push to the server
- `/pr` — stage changes, write a commit message, and open a pull request

### Hooks

Hooks let you run custom scripts at specific points in Cline's execution lifecycle — for example, automatically running a formatter after every file edit. Hooks are enabled or disabled by setting file permissions (`chmod +x` to enable, `chmod -x` to disable).

![Cline Hooks](images/Cline%20Hooks.png)

- **Global Hooks** apply across all workspaces.
- **Workspace Hooks** apply only to the current project (stored in `.clinerules/hooks/`).

### Skills

Skills are reusable instruction sets that Cline loads on demand. When a task matches a skill's description, Cline automatically invokes the `use_skill` tool to load the full instructions for that skill.

![Cline Skills](images/Cline%20Skills.png)

- **Global Skills** are available in any workspace.
- **Workspace Skills** are specific to the current project.

---

## Using MCP Tools (RAG Index Access)

When the MCP server is connected and **Use MCP servers** is enabled (either via auto-approve or manual approval), Cline can search your RAG indexes as part of answering a question.

You do not need to invoke tools manually — Cline decides when to use them based on your request. If you want to target a specific index, be explicit:

> "Search the `ipp-documentation` index for information about the API authentication flow."

To see which MCP tools are currently available, click the ![Cline MCP servers icon](images/cline-mcp.png) icon in the Cline toolbar. Each tool corresponds to one of your configured indexes or other MCP-connected services.

---

## Tips

- **Be specific.** "Fix the bug in `auth.py` where the token expires too early" works better than "fix the bug."
- **Use Plan mode for multi-step tasks.** Let Cline lay out the approach before it starts touching files.
- **Start a new chat when switching tasks.** Context from previous conversations carries over and can confuse Cline on unrelated work.
- **Keep conversations short.** Very long sessions consume more tokens and can degrade response quality. Start fresh if a chat has gone on for a long time.
- **Follow up with corrections.** If an edit is almost right, say so: "That's close, but don't rename the existing variables." Cline will revise.
- **Use workspace rules for project conventions.** Rather than repeating "use 4-space indentation" every session, put it in a workspace rule file.
