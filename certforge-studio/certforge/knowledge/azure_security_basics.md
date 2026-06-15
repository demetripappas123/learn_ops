# Azure Security Basics

**Tags:** AZ-204, Security, Managed Identity, Entra ID

## Summary

Azure Security Basics establishes foundational principles for securing applications and resources in Microsoft Azure. This knowledge domain covers identity and access management through managed identities and Entra ID (Azure AD), principle of least privilege implementation, elimination of hardcoded secrets and connection strings, and Role-Based Access Control (RBAC) for fine-grained authorization. Mastering these concepts is essential for developing secure Azure applications that comply with security best practices and reduce attack surface by removing credential management overhead from application code.

## Key Concepts

### Managed Identity

Managed identity is an Azure feature that provides applications and resources with automatic identity provisioning and credential management without storing secrets in code or configuration files. There are two types: system-assigned managed identities, which are created and bound to a specific Azure resource with the same lifecycle, and user-assigned managed identities, which are standalone resources that can be shared across multiple services. Managed identities integrate seamlessly with Azure services through Entra ID, enabling applications to authenticate to Azure resources, databases, Key Vault, and other services without hardcoding credentials. The underlying token refresh and lifecycle management is handled entirely by Azure, reducing operational complexity and security risks associated with credential rotation.

### Least Privilege

Least privilege is a security principle that restricts user, application, and service access to only the minimum permissions necessary to perform their intended functions. In Azure, this means granting specific RBAC roles with limited scope rather than broad administrative access. Applications should request only the API permissions they require, managed identities should be assigned to specific resources and scopes, and custom roles can be created to define granular permissions. Implementing least privilege reduces blast radius in case of compromise, prevents accidental misuse of elevated permissions, and ensures audit trails remain focused on purposeful actions rather than noise from overprivileged operations.

### No Hardcoded Secrets

Hardcoding secrets such as connection strings, API keys, passwords, and access tokens directly in application source code is a critical security vulnerability. Secrets in code are visible to anyone with repository access, may be exposed in logs and error messages, are difficult to rotate without code changes and redeployment, and persist in version control history even after deletion. Azure provides alternatives including Azure Key Vault for centralized secret storage with encryption, managed identities for certificate-free authentication, environment variables and configuration files for deployment-time secret injection, and secrets management tools integrated with CI/CD pipelines. Applications should retrieve secrets at runtime from secure storage rather than embedding them during development.

### RBAC (Role-Based Access Control)

RBAC is Azure's authorization mechanism that assigns permissions to identities (users, groups, service principals, managed identities) at specific scopes (subscriptions, resource groups, individual resources). Built-in roles include Owner, Contributor, Reader, and service-specific roles like Storage Blob Data Reader or SQL Server Contributor. RBAC follows the permission model of actions permitted at each role level, with explicit Allow statements and Deny rules taking precedence over inherited permissions. Custom roles can be created to define exact permission sets needed for specific job functions. RBAC evaluation occurs at every Azure API call, ensuring authorization is enforced consistently across all resource interactions and supporting detailed audit logging of access decisions.

## Project Applications

Managed identities and Azure Security Basics principles are applied throughout enterprise Azure projects to eliminate credential management from application code. A compute service such as an Azure Function App or Virtual Machine with a managed identity can authenticate to Azure SQL Database, Azure Storage, or Cosmos DB without storing connection strings in the application configuration. Key Vault access policies can limit managed identity access to specific keys, certificates, and secrets. Web applications can use managed identities to securely call downstream Azure services and third-party APIs with delegated Entra ID tokens. RBAC policies ensure that development teams have appropriate access to development resources, production support teams have read-only or limited-scope access to production resources, and automation accounts have minimal permissions to perform only required operations. Configuration management and environment-specific settings are separated from secrets, enabling secure deployment pipelines where no human ever touches production secrets directly.

## Assessment Seeds

**Prompt 1: Managed Identity Authentication Decision**

Your team is building a .NET web application deployed to Azure App Service that needs to connect to an Azure SQL Database. You have two options: store the SQL connection string in the App Service configuration settings, or configure a system-assigned managed identity on the App Service and use token-based authentication to the database. Compare these approaches in terms of security posture, credential lifecycle management, scalability, and operational overhead. Why is managed identity the preferred solution for this scenario, and what are the implementation steps?

**Prompt 2: RBAC and Least Privilege Implementation**

Design an RBAC strategy for a development team that includes frontend developers, backend developers, DevOps engineers, and QA testers. Each role has different needs: frontend developers should modify only web app resources, backend developers require access to databases and APIs, DevOps engineers need to manage infrastructure and deployments, and QA testers need read-only access to test environments. Specify the built-in roles, custom roles if needed, and scope assignments for each team member. How would you prevent a compromised frontend developer account from accessing production resources?

**Prompt 3: Hardcoded Secrets Remediation**

Audit the following legacy application configuration: a database connection string stored in appsettings.json, an API key for a third-party service in environment variables on the deployment server, and a personal access token cached in application memory for GitHub Actions authentication. Identify security vulnerabilities in each case, explain the risks of exposure, and design a migration path to Azure Key Vault with managed identity authentication. What are the breaking changes to the application, and how should the deployment pipeline be updated?
