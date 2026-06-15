# CertForge Studio — Azure Handover & Wiring Guide

**Audience:** the developer configuring the Azure pipeline.
**Goal:** stand up the Azure services CertForge Studio needs, deploy the Streamlit
app to **Azure Container Apps**, and hand back a small set of values the app reads
from the environment.

CertForge is **secure-by-default and degrades gracefully**: with no Azure config it
runs fully local and deterministic. You are turning on two optional capabilities:

| Capability | Service | Flag | Required for demo? |
| --- | --- | --- | --- |
| **Foundry IQ grounding** (retrieval) | **Azure AI Search** | `USE_FOUNDRY_IQ=true` | ✅ yes (the default Azure demo) |
| **LLM agent enrichment** | **Azure OpenAI in Foundry Models** (`gpt-4o`) | `USE_FOUNDRY_LLM=true` | ⬜ optional |
| **Hosting the UI** | **Azure Container Apps** | — | ✅ yes |

> **Why Azure AI Search = "Foundry IQ":** Foundry IQ is Microsoft's agentic-retrieval
> knowledge layer, and per Microsoft Learn it is **built on Azure AI Search**
> ("Is Azure AI Search required for Foundry IQ? Yes."). We index the knowledge docs
> into Azure AI Search; that index is the foundation a full Foundry IQ *knowledge base*
> sits on. See the upgrade path in §9.

---

## 0. TL;DR for the pipeline developer

1. Create a resource group, an **Azure AI Search** service (Basic tier, RBAC enabled),
   and (optional) an **Azure OpenAI** resource with a `gpt-4o` deployment.
2. Build the image with **`az acr build`** (no local Docker needed) and deploy to
   **Container Apps** with a **system-assigned managed identity**, target port **8501**.
3. Grant the app's managed identity **`Search Index Data Reader`** on Search (and
   **`Cognitive Services OpenAI User`** on OpenAI if using the LLM), plus **`AcrPull`** on the registry.
4. Set the env vars from §6 on the container app.
5. Run `python scripts/index_knowledge.py` once to load the knowledge docs into the index.
6. Hand back the values in the **§10 checklist**.

---

## 1. Prerequisites

```bash
az login
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"

# Container Apps tooling + providers
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.Search
az provider register --namespace Microsoft.CognitiveServices
```

Set reusable shell variables (edit these):

```bash
RG=certforge-rg
LOC=eastus
SEARCH=certforge-search-$RANDOM      # must be globally unique, lowercase
ACR=certforgeacr$RANDOM              # 5-50 alphanumerics, globally unique
ENVNAME=certforge-env
APP=certforge
INDEX=certforge-knowledge
# Optional LLM:
AOAI=certforge-aoai-$RANDOM
MODEL=gpt-4o
```

```bash
az group create --name $RG --location $LOC
```

---

## 2. Azure AI Search (the Foundry IQ grounding) — REQUIRED

```bash
# Basic tier or higher is required for RBAC/keyless auth.
az search service create \
  --name $SEARCH --resource-group $RG --location $LOC \
  --sku basic --partition-count 1 --replica-count 1

# Enable Microsoft Entra (RBAC) auth ("aadOrApiKey" allows both keys and RBAC).
# Requires a recent Azure CLI; if the flag is unrecognised, use the portal toggle below.
az search service update --name $SEARCH --resource-group $RG \
  --auth-options aadOrApiKey
```

> Portal equivalent: **Search service → Settings → Keys → "Role-based access control"
> or "Both"**.

Capture the endpoint (used as `AZURE_SEARCH_ENDPOINT`):

```bash
SEARCH_ENDPOINT="https://$SEARCH.search.windows.net"
SEARCH_ID=$(az search service show --name $SEARCH --resource-group $RG --query id -o tsv)
echo $SEARCH_ENDPOINT
```

**Keys (optional — only if you prefer key auth over managed identity):**

```bash
# ADMIN key (needed by the indexing script if you load via key)
az search admin-key show --service-name $SEARCH --resource-group $RG --query primaryKey -o tsv
# QUERY key (read-only, for the running app if using key auth)
az search query-key list --service-name $SEARCH --resource-group $RG --query "[0].key" -o tsv
```

---

## 3. Load the knowledge index (Foundry IQ content)

The repo ships a loader: **`scripts/index_knowledge.py`**. It creates an index named
`$INDEX` with fields `id, title, source, content` and uploads the five Markdown docs in
`certforge/knowledge/`.

Run it once from a machine that has the repo + the Azure extras, using **either** an
admin key **or** your own `az login` identity (which needs `Search Service Contributor`
+ `Search Index Data Contributor` on the search service):

```bash
pip install -r requirements-azure.txt
export AZURE_SEARCH_ENDPOINT="$SEARCH_ENDPOINT"
export AZURE_SEARCH_INDEX_NAME="$INDEX"
# Key auth (optional): export AZURE_SEARCH_API_KEY="<ADMIN_KEY>"
python scripts/index_knowledge.py
# -> Index 'certforge-knowledge' created/updated.
# -> Uploaded 5/5 documents to index 'certforge-knowledge'.
```

If using your own identity instead of a key:

```bash
ME=$(az ad signed-in-user show --query id -o tsv)
az role assignment create --assignee-object-id $ME --assignee-principal-type User \
  --role "Search Service Contributor"    --scope $SEARCH_ID
az role assignment create --assignee-object-id $ME --assignee-principal-type User \
  --role "Search Index Data Contributor" --scope $SEARCH_ID
```

---

## 4. (OPTIONAL) Azure OpenAI in Foundry Models — for `USE_FOUNDRY_LLM=true`

```bash
az cognitiveservices account create \
  --name $AOAI --resource-group $RG --location $LOC \
  --kind OpenAI --sku S0 --yes

# Discover an available gpt-4o version in your region (avoids a fragile hard-coded pin):
MVER=$(az cognitiveservices model list -l $LOC \
  --query "max_by([?model.name=='gpt-4o'], &model.version).model.version" -o tsv)
echo "Using gpt-4o version: $MVER"

az cognitiveservices account deployment create \
  --name $AOAI --resource-group $RG \
  --deployment-name $MODEL \
  --model-name gpt-4o --model-version "$MVER" --model-format OpenAI \
  --sku-name Standard --sku-capacity 10

AOAI_ENDPOINT=$(az cognitiveservices account show --name $AOAI --resource-group $RG --query properties.endpoint -o tsv)
AOAI_ID=$(az cognitiveservices account show --name $AOAI --resource-group $RG --query id -o tsv)
echo $AOAI_ENDPOINT   # -> https://<name>.openai.azure.com/
```

> `AZURE_OPENAI_DEPLOYMENT` is the **deployment name** you chose (`$MODEL`), not the model name.

---

## 5. Build the image and deploy to Container Apps

### 5.1 Build in the cloud (no local Docker required)

```bash
az acr create --name $ACR --resource-group $RG --sku Basic
# Run from the certforge-studio/ directory (where the Dockerfile lives):
az acr build --registry $ACR --image certforge:latest .
ACR_ID=$(az acr show --name $ACR --resource-group $RG --query id -o tsv)
```

### 5.2 Create the Container Apps environment

```bash
az containerapp env create --name $ENVNAME --resource-group $RG --location $LOC
```

### 5.3 Create the app with a system-assigned identity (bootstrap on a public image)

```bash
az containerapp create \
  --name $APP --resource-group $RG --environment $ENVNAME \
  --image mcr.microsoft.com/k8se/quickstart:latest \
  --target-port 8501 --ingress external --system-assigned

PRINCIPAL_ID=$(az containerapp show --name $APP --resource-group $RG \
  --query identity.principalId -o tsv)
echo $PRINCIPAL_ID
```

### 5.4 Grant the managed identity its roles

```bash
# Pull the image from ACR
az role assignment create --assignee-object-id $PRINCIPAL_ID --assignee-principal-type ServicePrincipal \
  --role "AcrPull" --scope $ACR_ID

# Query Azure AI Search at runtime (read-only)
az role assignment create --assignee-object-id $PRINCIPAL_ID --assignee-principal-type ServicePrincipal \
  --role "Search Index Data Reader" --scope $SEARCH_ID

# OPTIONAL: call the model (only if USE_FOUNDRY_LLM=true)
az role assignment create --assignee-object-id $PRINCIPAL_ID --assignee-principal-type ServicePrincipal \
  --role "Cognitive Services OpenAI User" --scope $AOAI_ID
```

### 5.5 Point the app at our private image (pull via managed identity)

```bash
az containerapp registry set --name $APP --resource-group $RG \
  --identity system --server $ACR.azurecr.io

az containerapp update --name $APP --resource-group $RG \
  --image $ACR.azurecr.io/certforge:latest
```

### 5.6 Set the app environment variables

**Default demo (deterministic + Azure AI Search grounding):**

```bash
az containerapp update --name $APP --resource-group $RG --set-env-vars \
  USE_FOUNDRY_IQ=true \
  AZURE_SEARCH_ENDPOINT=$SEARCH_ENDPOINT \
  AZURE_SEARCH_INDEX_NAME=$INDEX
```

**To also enable the LLM agents (optional):**

```bash
az containerapp update --name $APP --resource-group $RG --set-env-vars \
  USE_FOUNDRY_LLM=true \
  AZURE_OPENAI_ENDPOINT=$AOAI_ENDPOINT \
  AZURE_OPENAI_DEPLOYMENT=$MODEL
```

> The container uses **managed identity by default** (no keys in env). The app reads
> `AZURE_SEARCH_API_KEY` / `AZURE_OPENAI_API_KEY` only if you choose to set them.

### 5.7 Verify

```bash
az containerapp show --name $APP --resource-group $RG \
  --query properties.configuration.ingress.fqdn -o tsv       # -> open https://<fqdn>
az containerapp logs show --name $APP --resource-group $RG --follow
```

In the running app's sidebar you should see:
`Grounding: Azure AI Search (Foundry IQ)  ·  Agents: Deterministic`.

---

## 6. Environment variable contract (what the app reads)

| Variable | Required | Example | Notes |
| --- | --- | --- | --- |
| `USE_FOUNDRY_IQ` | for Search | `true` | turns on Azure AI Search retrieval |
| `AZURE_SEARCH_ENDPOINT` | for Search | `https://certforge-search.search.windows.net` | service Overview |
| `AZURE_SEARCH_INDEX_NAME` | for Search | `certforge-knowledge` | created by the loader |
| `AZURE_SEARCH_API_KEY` | optional | _(blank)_ | leave blank for managed identity |
| `USE_FOUNDRY_LLM` | for LLM | `true` | turns on Azure OpenAI enrichment |
| `AZURE_OPENAI_ENDPOINT` | for LLM | `https://certforge-aoai.openai.azure.com/` | resource endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | for LLM | `gpt-4o` | deployment name |
| `AZURE_OPENAI_API_KEY` | optional | _(blank)_ | leave blank for managed identity |
| `AZURE_OPENAI_API_VERSION` | optional | `2024-10-21` | default is fine |

The local template is `.env.example` (copy to `.env` for local runs).

---

## 7. RBAC roles summary (keyless model)

| Identity | Role | Scope | Purpose |
| --- | --- | --- | --- |
| Container App managed identity | `AcrPull` | Container Registry | pull the image |
| Container App managed identity | `Search Index Data Reader` | Azure AI Search | query at runtime |
| Container App managed identity | `Cognitive Services OpenAI User` | Azure OpenAI | call the model (LLM only) |
| Human/CI running the loader | `Search Service Contributor` + `Search Index Data Contributor` | Azure AI Search | create + load the index |

---

## 8. Local run with keys (for the app developer)

Once you hand back the values, the app dev can run locally:

```bash
cp .env.example .env        # then fill in the values below
# .env:
#   USE_FOUNDRY_IQ=true
#   AZURE_SEARCH_ENDPOINT=https://<search>.search.windows.net
#   AZURE_SEARCH_INDEX_NAME=certforge-knowledge
#   AZURE_SEARCH_API_KEY=<query key>          # OR run `az login` and leave blank
pip install -r requirements.txt -r requirements-azure.txt
streamlit run app.py
```

---

## 9. Upgrade path: from a Search index to a full Foundry IQ knowledge base

The app uses Azure AI Search's standard keyword/semantic query today (GA, simplest).
To graduate to full **Foundry IQ agentic retrieval** later:

1. Create a **knowledge base** in Azure AI Search over the same index (or over Blob
   Storage as an indexed knowledge source).
2. (Optional) Attach a `gpt-4o`/`gpt-4.1`/`gpt-5` deployment for LLM **query planning**.
3. Swap `certforge/foundry/search_client.py` to call the knowledge base retrieval API
   (`KnowledgeBaseRetrievalClient`) instead of `SearchClient.search`. The rest of the
   app is unchanged because retrieval is isolated behind one function.

---

## 10. Handback checklist (return these to the app team)

- [ ] `AZURE_SEARCH_ENDPOINT` = `https://__________.search.windows.net`
- [ ] `AZURE_SEARCH_INDEX_NAME` = `certforge-knowledge` (confirm 5 docs uploaded)
- [ ] (if key auth) `AZURE_SEARCH_API_KEY` = query key
- [ ] (LLM) `AZURE_OPENAI_ENDPOINT` = `https://__________.openai.azure.com/`
- [ ] (LLM) `AZURE_OPENAI_DEPLOYMENT` = `gpt-4o`
- [ ] (LLM, if key auth) `AZURE_OPENAI_API_KEY`
- [ ] Container App URL (FQDN) = `https://__________`
- [ ] Confirmed sidebar shows `Grounding: Azure AI Search (Foundry IQ)`

---

## 11. Cost & cleanup

- **Azure AI Search Basic** and **Container Apps** (scale-to-zero) are inexpensive for a
  demo; **Azure OpenAI** bills per token. Delete everything with:

```bash
az group delete --name $RG --yes --no-wait
```

## 12. Security / Responsible AI notes

- Keyless **managed identity** is the default; no secrets live in code or the image.
- The image runs as a **non-root** user.
- Only **synthetic** learner/workload data is used; no PII.
- Assessment questions are original and locally authored — the LLM only expands
  *explanatory* text, never generates exam questions.
