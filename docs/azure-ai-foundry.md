## Azure AI Foundry

**Purpose:**  

Azure AI Foundry is a unified cloud platform where developers build, test, and manage enterprise AI applications. It acts as a centralized workspace that connects AI models to your organization's data, storage, and security infrastructure.

**Endpoint:** `https://aifoundry0436939217.openai.azure.us`  

---

## Part 1: Management Center (Hub Level) Setup
The Management Center is the administrative control plane used for governance, security, and capacity planning.

## Step 1: Create an Azure AI Foundary

1. Search for `Azure AI Foundary` in the search bar at the top of the portal
2. Click **+ Create** and select **Hub**
3. Basics Tab

    - Select a resource group
    - Ensure the Region is USGov Virginia
    - SelectAI services to include in the Hub
    
4. Storage Tab

  * Select a storage account. You can create a new storage resource or select one that was already made
  * Credential store - select Azure Key Vault and create a new Key vault.
  * Application Insights: This is required for logging and monitoring. Click **Create new** to provision a dedicated instance for this Hub.
  * Container registry - *(Optional)* Select your existing Container Registry only if you plan to use custom Docker environments. Otherwise, you can leave this as **None**.

5. Inbound Access Tab - Select **All networks**
6. Outbound Access Select **Public**
7. Encryption Tab - Leave as default (Microsoft-managed keys) unless your agency requires a Customer-managed key.
8. Review + Create - Review your configurations and click **Create** to provision the Hub.

## Step 2: Create a Project Workspace

1. Once the Hub is deployed, click **Go to resource** and launch the **Azure AI Foundry** at the bottom of the page.
2. From the Hub menu, click **+ New project**
3. Enter a Project Name (e.g., `llms-virginia`).
4. Verify it is linked to the Hub you just created.
5. Click **Create** to provision the isolated developer workspace.

## Step 3: Link RAG Resources

1. Inside your new Project, navigate to **Data + indexes** in the left sidebar.
2. Under the Indexes tab, click **+ New index**.
3. Select and link **Azure AI Search** (this is required to host your vector indexes for your RAG website).
4. Click **Next** and for *Select Azure AI Search service*, select **Connect other Azure AI Search resource** 
5. Verify that your search service resource you want to add has *API key authentication* and click **Add Connection**
6. This will take you back to the last page. Select your Azure AI Search Service resource
7. Select the desired index for your project
8. *(Optional)* Link an **Azure Container Registry** if you need to store custom Docker images for your environments.

## Step 4: Deploy an AI Model

1. In the Project workspace, navigate to **Models + Endpoints** on the left menu.
2. Click **+ Deploy model**.
3. Choose an available Azure OpenAI model (e.g., `gpt-4`). *Note: Open-source models are not available in the Gov region.*
4. Enter a Deployment name (e.g., `gpt-4o-virginia`). 
5. Select a Deployment type *Note: Standard allows 80,000 tokens and Data Zone Standard allows 50,000 tokens*
5. Click **Customize** to adjust your Tokens Per Minute (TPM) slider based on your granted quota.
6. Click **Deploy**. Once finished, copy the **Endpoint URL** and **API Key** to use in your Python routing application.

## Step 5: Locate Your Connection Details

To connect your custom Python applications to your deployed models, you need to gather your specific connection details.

1. **Find your Project Endpoint:**

   * In the Azure AI Foundry portal, navigate to your Project (e.g., `llms-virginia`).
   * Go to the **Overview** page. 
   * Look for the **Project endpoint** (or Project connection string) in the Project details section. It will look similar to `https://<your-project-name>.<region>.inference.ai.azure.com` or `https://<resource>.services.ai.azure.com/api/projects/<project-name>`. 
   * Copy this value; it is required to initialize the `AIProjectClient` in your Python code.

2. **Find your Model Endpoint and API Keys:**

   * In your Project workspace, navigate to **Models + endpoints** on the left menu.
   * Select the deployment you just created (e.g., `gpt-4o-virginia`).
   * Here you will find the specific **Endpoint Target URL** (ending in `.azure.us` for the Gov cloud) and the **API Key** required to authenticate your API calls.

*(Note: Depending on your application's setup, you may also need the connection details for the Azure AI Search resource you linked earlier. You can find this by clicking on that specific connection under the **Connected resources** menu.)*

