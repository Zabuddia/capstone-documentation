# Azure AI Foundry

**Purpose:**  

Azure AI Foundry is a unified cloud platform where developers build, test, and manage enterprise AI applications. It acts as a centralized workspace that connects AI models to your organization's data, storage, and security infrastructure.

**Endpoint:** `https://aifoundry0436939217.openai.azure.us`  

---

## Part 1: Management Center (Hub Level) Setup
The Management Center is the administrative control plane used for governance, security, and capacity planning.

## Step 1: Create an Azure AI Foundry

1. Search for `Azure AI Foundry` in the search bar at the top of the portal
2. Click **+ Create** and select **Hub**
3. Basics Tab

    - Select a resource group
    - Ensure the Region is USGov Virginia
    - Create a Name for the Hub
    - Create a new AI service to include in the Hub
    
4. Storage Tab

      * Select a storage account. You can create a new storage resource or select one that was already made
      * Credential store - select Azure Key Vault and create a new Key vault.
      * Application Insights: This is required for logging and monitoring. Click **Create new** to provision a dedicated instance for this Hub.
      * Container registry - leave this as **None**.

5. Inbound Access Tab - Select **All networks**
6. Outbound Access - Select **Public**
7. Encryption Tab - Leave as default (Microsoft-managed keys) unless your agency requires a Customer-managed key.
8. Review + Create - Review your configurations and click **Create** to provision the Hub.

## Step 2: Create a Project Workspace

1. Once the Hub is deployed, click **Go to resource** and launch the **Azure AI Foundry** at the bottom of the page.
2. From the Hub menu, click **+ New project**
3. Enter a Project Name (e.g., `llms-virginia`).
4. Verify it is linked to the Hub you just created.
5. Click **Create** to provision the isolated developer workspace.

## Step 3: Deploy an AI Model

1. In the Project workspace, navigate to **Models + Endpoints** on the left menu.
2. Click **+ Deploy model**.
3. Choose an available Azure OpenAI model (e.g., `gpt-4`) and click **Confirm**. *Note: Token per Minute rate differs by model*
4. Enter a Deployment name (e.g., `gpt-4o-virginia`). 
5. Select a Deployment type *Note: Select either Standard or Data Zone Standard*
5. Click **Customize** to adjust your Tokens Per Minute (TPM) slider based on your granted quota.
6. Click **Deploy**. Once finished, copy the **Endpoint URL** and **API Key** to use in your Python routing application.

## Step 4: Locate Endpoints and Keys

To connect your custom Python applications to your deployed models, you need to gather your specific connection details.

   1. In the Azure AI Foundry portal, navigate to your Project (e.g., `llms-virginia`).
   2. Go to the **Overview** page. 
   3. Look for the **Project endpoint** in the Endpoints and Keys section. 
   4. This is the Azure OpenAI Endpoint. It will look similar to `https://ai-aifoundry<regions><ID_numbers>.openai.azure.us/` 
   5. Look for the API Key. Should be near the top of the page.

*(Note: Depending on your application's setup, you may also need the connection details for the Azure AI Search resource you linked earlier. You can find this by clicking on that specific connection under the **Connected resources** menu.)*

