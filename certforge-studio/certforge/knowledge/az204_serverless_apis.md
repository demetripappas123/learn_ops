# AZ-204 Serverless APIs

Tags: AZ-204, Azure Functions, APIs, serverless

## Summary

Azure Functions enables developers to build serverless APIs and event-driven applications without managing infrastructure. The platform abstracts server management, automatically scales based on demand, and charges only for compute time consumed. Azure Functions integrates with HTTP triggers to create scalable REST endpoints, supports multiple language runtimes, and provides built-in bindings for seamless integration with other Azure services. Key competencies for AZ-204 include designing and implementing triggered functions, creating HTTP-based APIs, managing function app configuration, implementing authentication and authorization, and monitoring application health and performance. Serverless architectures reduce operational overhead, enable rapid deployment cycles, and allow developers to focus on business logic rather than infrastructure concerns.

## Key Concepts

### Function Triggers

Triggers determine when a function executes. Azure Functions supports multiple trigger types that enable different event-driven patterns. HTTP triggers expose functions as REST endpoints accessible over the internet, supporting GET, POST, PUT, DELETE, and other HTTP methods. Timer triggers execute functions on a schedule using cron expressions, enabling periodic batch operations and maintenance tasks. Blob triggers activate when files are uploaded or modified in Azure Storage containers, supporting file processing workflows. Queue triggers respond to messages in Azure Storage queues or Azure Service Bus, enabling asynchronous message processing and decoupling of services. Event Grid triggers connect to Azure Event Grid for reactive event handling. Event Hub triggers process streaming data from Azure Event Hubs. Service Bus triggers handle messaging from Azure Service Bus queues and topics.

### HTTP Endpoints and REST API Design

HTTP triggers transform Azure Functions into REST API endpoints. Functions receive HTTP requests with query parameters, route parameters, and request body data. Azure Functions routing supports parameterized paths using curly braces, enabling RESTful resource identification patterns. Route parameters are accessible through function parameters or bindings. HTTP responses are constructed with status codes, headers, and response bodies. Authorization decorators control access to endpoints through API keys, function keys, or Azure AD authentication. CORS (Cross-Origin Resource Sharing) policies manage browser-based client access. Response headers support caching directives, content negotiation, and security headers. Developers define function contracts through input and output bindings, transforming declarative configurations into executable logic.

### Input and Output Bindings

Bindings connect functions to external services declaratively, reducing boilerplate code and enabling framework-level optimizations. Input bindings read data from external services before function execution, including HTTP requests, queue messages, and database records. Output bindings send function results to external destinations after execution, writing to storage accounts, queues, databases, or notification services. Blob bindings interact with Azure Storage Blobs, supporting read and write operations on blob content. Queue bindings produce and consume messages in Azure Storage queues and Service Bus entities. Table bindings perform CRUD operations on Azure Table Storage. Cosmos DB bindings query and write documents to Azure Cosmos DB collections. Timer bindings receive schedule metadata. Service Bus bindings send messages to queues and topics. Bindings are declared in function.json configuration files (consumption plan) or as decorator attributes (isolated worker model), specifying parameter names, connection strings, and data paths.

### Blob Triggers and File Processing

Blob triggers execute functions when blobs are created or updated in Azure Storage containers. Trigger metadata includes blob name, size, and path, enabling functions to identify and process specific files. Scalability is managed through checkpoint storage, preventing duplicate processing of the same blob. Functions receive blob content as stream objects, enabling efficient processing of large files without loading entire contents into memory. Blob bindings support reading existing blobs and writing output blobs to storage containers. Common patterns include image processing workflows, document conversion pipelines, and log file analysis. Blob triggers integrate with Azure Functions runtime to automatically retrieve and process blobs as they arrive. Error handling and retry policies ensure resilience when processing fails. Batch processing capabilities enable functions to handle multiple blobs efficiently.

### Configuration and Runtime Settings

Function app settings control runtime behavior and provide configuration values to functions. Settings are stored in Azure Key Vault for sensitive data like connection strings and API keys. Local development uses local.settings.json files containing environment variables and connection strings accessible at function startup. Production environments use Azure Key Vault integration and Azure App Configuration for centralized configuration management. Environment variables are accessed through function parameters or System.Environment calls. Application Insights integration enables logging, tracing, and performance monitoring. Function timeouts, memory allocation, and runtime versions are configured at the function app level. App Service Plan and Consumption Plan selections determine scaling behavior and cost models. Custom handlers enable functions to run in languages not natively supported by the Azure Functions runtime.

### Authentication and Authorization

Function authorization is enforced through API keys, Azure AD token validation, and role-based access control. Function keys are endpoint-specific credentials enabling function invocation without exposing code. Host keys provide shared authorization across all functions in an app. Anonymous authorization allows public access without credentials. Azure AD integration verifies OAuth tokens and extracts user identity claims. Managed identities enable functions to authenticate to Azure services without storing credentials. Decorators and annotations apply authorization policies to function definitions. Custom authorization handlers validate incoming requests against business logic rules. Secure by default approaches minimize exposure of publicly accessible endpoints.

### Monitoring and Observasting

Application Insights provides comprehensive monitoring of function execution health, performance, and errors. Telemetry data includes request counts, execution times, error rates, and custom metrics. Traces and logs capture function activity for debugging and auditing. Live Metrics Stream displays real-time execution data during development and troubleshooting. Log Analytics queries enable detailed analysis of patterns and anomalies. Alerts notify operators of performance degradation or error thresholds being exceeded. Profiler tools identify performance bottlenecks in function code. Dependency tracking visualizes calls to databases, APIs, and external services. Custom metrics instrument business-specific events and KPIs. Distributed tracing correlates logs across multiple functions and services in application workflows.

## Project Applications

Implementing serverless API solutions addresses numerous production requirements and architectural patterns:

Building REST APIs with HTTP triggers creates scalable endpoints for web and mobile applications without managing web servers. Query parameter validation and route constraints enforce contract compliance. Response caching strategies optimize performance for frequently accessed resources. Asynchronous function chains process long-running operations without blocking clients. Function orchestration through Durable Functions manages complex multi-step workflows with built-in resilience and state management.

File processing workflows triggered by blob uploads enable document processing, image transformation, and data pipeline automation. Event-driven architecture patterns decouple services using queues and topics, enabling independent scaling and failure isolation. Real-time notifications through Service Bus integration alert systems of important events. Rate limiting and throttling protect downstream services from overload.

Data synchronization pipelines use blob and queue triggers to replicate data across storage systems. Change Data Capture patterns propagate modifications to dependent services. Background job processing using timer and queue triggers handles batch operations outside request-response cycles.

## Assessment Seeds

**Prompt 1: API Architecture Decision**
Design a serverless API endpoint that accepts customer order data, validates the input, stores the order in Azure Cosmos DB, and sends a confirmation message to a Service Bus topic for downstream processing. What trigger type would you use for the primary endpoint? How would you structure input and output bindings? What authentication strategy would you implement? How would you monitor success and failure rates? Explain your choices and tradeoffs.

**Prompt 2: Blob Processing Pipeline**
Create a blob-triggered function that processes uploaded CSV files, transforms the data into JSON format, and writes output to another container. How would you handle large files efficiently without memory constraints? What error handling strategy would you implement for malformed CSV data? How would you prevent duplicate processing? What observability would you instrument? What scaling considerations would you address?

**Prompt 3: Multi-Service Integration**
Build an event-driven system where an HTTP-triggered function initiates a workflow: read configuration from Table Storage, retrieve data from a Cosmos DB collection, apply business logic transformations, write results to Blob Storage, and trigger a notification through Event Grid. What bindings would you declare? How would you structure error handling and retry logic? What performance optimizations would you implement? How would you test this integration locally?
