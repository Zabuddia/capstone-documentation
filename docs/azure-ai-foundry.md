# Azure AI Foundry

## Purpose

Create the Azure AI Foundry resources and model deployment used later by
LiteLLM and the RAG website.

## URL

Project endpoint: `https://<azure-openai-endpoint>.openai.azure.us/`

## Run Location

Azure portal.

## Before You Start

- An Azure Government subscription with permission to create AI resources
- A resource group in the target region
- Available model quota in the region where the deployment will run

## Context

This page creates three things: an Azure AI Foundry hub, a project attached to
that hub, and at least one deployed model. Later pages use the project
endpoint, deployment name, and API key from this setup.

## Steps

### Step 1: Create the Azure AI Foundry hub

1. In the Azure portal, search for **Azure AI Foundry**.
2. Click **+ Create** and choose **Hub**.
3. On the **Basics** tab:
    - Select the correct subscription and resource group.
    - Choose the target region, such as **USGov Virginia**.
    - Enter a hub name.
    - Create a new AI service for the hub.
4. On the **Storage** tab:
    - Select or create a storage account.
    - Set the credential store to **Azure Key Vault** and create one if needed.
    - Create a dedicated **Application Insights** instance.
    - Leave **Container registry** as **None** unless local requirements say
      otherwise.
5. On the **Inbound Access** tab, select **All networks**.
6. On the **Outbound Access** tab, select **Public**.
7. On the **Encryption** tab, keep the default setting unless a
   customer-managed key is required.
8. Review the configuration and create the hub.

### Step 2: Create the project workspace

1. Open the newly created hub.
2. Launch **Azure AI Foundry** from the hub page.
3. Select **+ New project**.
4. Enter a project name, such as `llms-virginia`.
5. Confirm that the project is linked to the correct hub.
6. Create the project.

### Step 3: Deploy an AI Model

1. In the project workspace, open **Models + Endpoints**.
2. Select **+ Deploy model**.
3. Choose the Azure OpenAI model that will be used later, such as `gpt-4o`.
   This is the **Model name** — the actual underlying model provided by Azure.
4. Enter a deployment name, such as `gpt-4o-virginia`.
   This is the **Deployment name** — a label you choose to identify this
   specific deployment. It can be anything, but something descriptive like
   `gpt-4o-virginia` makes it easier to manage multiple deployments.
5. Select the deployment type required for the environment.
6. Adjust the Tokens Per Minute setting if needed.
7. Create the deployment.

!!! note "Model name vs. Deployment name"
    These two values are used separately in LiteLLM's `config.yaml`:
    the **Deployment name** goes into `model: azure/<deployment-name>`, and the
    **Model name** goes into `base_model`. Both are recorded in Step 4 below.

!!! note "Deprecated models"
    Some models listed in the catalog cannot be deployed because they have been
    deprecated. If deployment fails with a `ServiceModelDeprecated` error, the
    selected model version is no longer available — choose a different model or
    a newer version. For example, `gpt-4` (version `1106-Preview`) was
    deprecated on 06/30/2025. Use `gpt-4o` or another active model instead.

### Step 4: Locate Endpoints and Keys

1. Open the project in Azure AI Foundry. If the hub page opens instead of the
   project, click **Go to project** to enter the project workspace.
2. Go to the **Models + Endpoints** page.
3. Click **Get endpoint**.
4. Copy the **Azure AI model inference endpoint**.
5. Copy the **Key**.
6. Record the **Model name**.

## What You Just Set Up

Azure AI Foundry is now ready for the rest of the stack. The project contains a
deployed model, and the project endpoint, API key, and deployment name are
available for the LiteLLM and RAG website configuration pages.
