# Automations & SLA Rules — FAQ

## What is the Automation Engine?

The Automation Engine lets you create **if-this-then-that** rules that trigger on ticket events. It eliminates repetitive manual tasks like assigning tickets, sending acknowledgments, or escalating overdue issues.

## What can trigger an automation?

Automations can be triggered by:
- **Ticket created** — fires when a new ticket arrives
- **Ticket updated** — fires when any field changes
- **Time-based** — fires after a specified time has passed (e.g., "ticket open for more than 2 hours")
- **Message received** — fires when a customer replies to a ticket

## What actions can automations perform?

- Assign ticket to an agent or team
- Add or remove a tag
- Change ticket status or priority
- Send an email reply (using a canned response template)
- Send an internal note
- Trigger a webhook

## How many automations can I have?

- Starter: up to 10 automation rules
- Growth: up to 100 automation rules
- Enterprise: unlimited

## What are SLAs?

SLAs (Service Level Agreements) define the maximum time allowed to **first respond** to and **resolve** a ticket, based on its priority.

Default SLA policy:

| Priority | First Response | Resolution  |
|----------|---------------|-------------|
| Urgent   | 1 hour        | 4 hours     |
| High     | 4 hours       | 8 hours     |
| Medium   | 8 hours       | 24 hours    |
| Low      | 24 hours      | 72 hours    |

SLA timers pause outside configured business hours unless you enable **24/7 SLA mode**.

## Can I create custom SLA policies?

Yes. Growth and Enterprise plans support multiple custom SLA policies. You can assign different SLAs to different teams, ticket types, or customer segments.

## What happens when an SLA is breached?

When an SLA is about to breach (configurable warning threshold, default 15 minutes before), NovaDesk:
1. Sends an email alert to the assigned agent and team lead.
2. Flags the ticket with a red SLA badge.

After breach, the ticket is marked **SLA Breached** in reports.

## Can I pause SLA timers?

Yes. Setting a ticket to **On Hold** status pauses the SLA timer. This is useful when you're waiting on a third-party vendor or waiting for the customer to provide more information.
