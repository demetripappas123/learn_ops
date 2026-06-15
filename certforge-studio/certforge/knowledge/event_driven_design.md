# Event-Driven Design

**Tags:** AZ-204, Event Driven Architecture, Blob Storage, Functions

## Summary

Event-driven design is an architectural pattern where applications react to events occurring within a system or between systems. Rather than direct synchronous communication, components publish events when state changes occur, and other components subscribe to and handle those events asynchronously. This decouples producers from consumers, enables scalability, and supports complex workflows across distributed systems. In Azure, event-driven architectures leverage services like Event Grid, Event Hubs, Service Bus, and Azure Functions to build responsive, resilient applications that scale dynamically.

## Key Concepts

### Event Source

An event source is the origin point that emits events when something notable happens. This could be Azure Blob Storage triggering an event when a file is uploaded, Azure Service Bus receiving a message, a custom application publishing a domain event, or an external system generating webhooks. Event sources act as publishers in the event-driven model, decoupling themselves from consumers by broadcasting events rather than calling handler methods directly. Azure Event Grid provides a managed service that acts as an event broker, connecting sources to subscribers seamlessly.

### Event Handler

An event handler is a consumer component that subscribes to specific event types and executes business logic when those events arrive. Azure Functions are a natural fit for event handlers, as they scale automatically and are triggered by bindings connected to event sources. Handlers should be stateless, idempotent, and focused on a single responsibility. They process events asynchronously, allowing the system to remain responsive and handle high throughput. Multiple handlers can subscribe to the same event, enabling pub-sub patterns where one event triggers parallel processing across different concern areas.

### Retries and Reliability

Event-driven systems must handle transient failures gracefully. Azure services provide built-in retry mechanisms with exponential backoff strategies. Event Grid and Service Bus support configurable retry policies that automatically reattempt failed deliveries over a specified duration. Functions can implement retry logic via Durable Functions, which provide orchestration and guaranteed execution semantics. Understanding retry policies prevents duplicate processing in some cases but requires idempotency guarantees in handlers. Monitoring and alerting on retry exhaustion helps identify systemic issues before they cascade through the system.

### Idempotency

Idempotency ensures that processing the same event multiple times produces the same result as processing it once. This is critical in distributed systems where retries, duplicate messages, or network failures can cause handlers to receive the same event multiple times. Idempotent handlers must track processed events using unique identifiers, check state before modifying data, or use conditional updates that atomically verify preconditions. Azure Cosmos DB, SQL Database, and Table Storage can all support idempotency checks. Designing handlers with idempotency in mind eliminates many reliability headaches and allows safe retry policies.

### Poison Queue

A poison queue is a dead-letter destination for messages or events that cannot be processed successfully, even after exhausting retry attempts. When an event handler fails repeatedly, the event is moved to a poison queue for manual investigation and remediation. Service Bus and Event Hubs automatically support dead-lettering. Poison queue handling enables systems to fail fast on a problematic message without blocking the entire pipeline. Operations teams monitor poison queues to detect application bugs, data corruption, or external service failures. Alerts on poison queue depth help maintain system health and prevent cascading failures.

## Project Applications

In the CertForge Studio certification project, event-driven design enables responsive exam workflows and audit trails:

**Exam Submission and Grading:** When an exam is submitted, an event triggers Azure Functions to validate answers, score responses, and persist results. Separate functions handle email notifications, analytics ingestion, and audit logging without coupling the submission handler to these concerns. Blob Storage upload events trigger document processing pipelines for uploaded study materials.

**Certification State Transitions:** As learners progress through certifications, state-change events trigger dependent workflows such as badge issuance, progress notifications, and prerequisite validations. Event Grid routes these events to Functions that update learner profiles, trigger payment workflows, or send milestone communications.

**Compliance and Audit Logging:** All significant operations emit audit events that Functions capture and log to durable storage. This creates an immutable record for compliance reviews without baking logging into every business handler. Dead-letter queues capture audit failures separately, preserving reliability of the certification core.

**Integration with External Systems:** Events published to Service Bus or Event Hubs integrate with third-party learning platforms, payment processors, and credential issuers. Decoupling via events allows swapping implementations without modifying core certification logic.

## Assessment Seeds

**Prompt 1: Idempotency Design**
You are designing an event handler that processes exam submission events and awards digital badges. The handler must be idempotent because submission events might be retried. Describe the mechanism you would use to detect and skip duplicate badge awards. What Azure service would store processed submission IDs, and how would you structure the check? Explain why unconditional badge issuance would violate system requirements and how your approach prevents duplicate credentials in the learner's profile.

**Prompt 2: Dead-Letter Queue Strategy**
A Function-based event handler that processes course enrollment events is failing 3% of the time due to intermittent dependencies. Enrollment events are being lost. Design a dead-lettering strategy using Service Bus poison queues. What should the handler do when it encounters a transient error versus an invalid event? How would you monitor and alert on poison queue depth, and what operational runbook would you create for an on-call engineer to remediate stuck enrollments?

**Prompt 3: Event Decoupling Trade-offs**
The CertForge system currently has a synchronous workflow where exam submission directly calls grade-checking logic, sends notifications, and records analytics in sequence. An architect proposes moving to event-driven architecture where submission triggers three independent Functions. What are the benefits and drawbacks? Consider consistency guarantees, latency, complexity, and observability. Under what conditions would event-driven be preferable, and what scenarios would synchronous coupling be simpler?
