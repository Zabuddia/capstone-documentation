# OpenWebUI User Guide

## Overview

OpenWebUI is a web-based chat interface for interacting with AI language models. It provides a clean, conversation-style UI similar to commercial AI chat products, but connected to your internal model infrastructure via LiteLLM. This guide covers everyday usage after OpenWebUI has been deployed.

---

## Prerequisites

- OpenWebUI is running and accessible on your network (see the Setup Guide)
- You have a user account (or the admin has enabled open registration)
- At least one model is configured and available through LiteLLM

---

## Logging In

1. Open a web browser and navigate to the OpenWebUI URL provided by your administrator.
2. Enter your username/email and password, then click **Sign In**.
3. If this is your first visit and registration is open, click **Register** to create an account.

---

## Starting a New Conversation

1. Click **New Chat** in the left sidebar (or the pencil/compose icon).
2. Select a model from the model picker at the top of the chat window.
3. Type your message in the input box at the bottom and press **Enter** or click the send button.

---

## Selecting a Model

The model picker dropdown at the top of the chat window lists all models available through your LiteLLM configuration. Different models have different strengths:

- **Larger models** — better reasoning and longer context, slower responses
- **Smaller/faster models** — quicker replies, good for simple tasks

You can switch models mid-conversation; the new model will apply to all subsequent messages in that chat.

---

## Conversation Features

### Editing Messages

Click the **pencil icon** next to any of your previous messages to edit and resend it. This will regenerate the AI's response from that point forward.

### Regenerating a Response

Click the **regenerate icon** below the AI's last message to get a new response to the same prompt. Useful when the first response isn't quite what you needed.

### Copying Responses

Click the **copy icon** below any response to copy the full text to your clipboard.

---

## Managing Conversations

### Viewing Chat History

Previous conversations appear in the left sidebar, sorted by most recent. Click any conversation to open it.

### Renaming a Conversation

Right-click a conversation in the sidebar and select **Rename**, or click the three-dot menu next to it. Give it a descriptive name so you can find it later.

### Deleting a Conversation

Right-click a conversation in the sidebar and select **Delete**, or use the three-dot menu. Deleted conversations cannot be recovered.

---

## Uploading Files

Some model configurations support file uploads (documents, images). To upload a file:

1. Click the **paperclip** or **attachment** icon in the message input area.
2. Select a file from your computer.
3. Type your question or instruction and send.

!!! note
    File upload support depends on the model and configuration. If the attachment icon is not visible, file uploads are not enabled for the current model.

---

## Settings and Customization

Click your username or avatar in the bottom-left corner to access settings:

- **Theme** — Switch between light and dark mode.
- **Default Model** — Set which model is selected when opening a new chat.
- **System Prompt** — Add a default system-level instruction that applies to all new conversations (e.g., "Always respond in plain language").

---

## Tips

- Give context upfront — the more background you provide, the more useful the response.
- For long or complex tasks, break them into multiple messages rather than sending everything at once.
- Use the conversation history to continue work across sessions rather than starting fresh each time.
- If a response is cut off, send "Continue" as your next message to prompt the model to keep going.
