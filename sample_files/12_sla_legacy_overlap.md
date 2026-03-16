# Understanding SLA Timers (Legacy Doc — May Be Outdated)

> ⚠️ **This article was written for NovaDesk v3.x. Some details may differ in v4.x. Refer to the Automations & SLA FAQ for the current configuration.**

## What is an SLA?

An SLA (Service Level Agreement) is a commitment to respond to or resolve a customer ticket within a set timeframe. NovaDesk measures two SLA metrics:

1. **First Response Time** — How quickly an agent first replies to the customer.
2. **Resolution Time** — How quickly the ticket is closed/resolved.

## Default SLA Times (v3.x — verify in your current settings)

| Priority | First Response | Resolution  |
|----------|---------------|-------------|
| Urgent   | 30 minutes    | 2 hours     |
| High     | 2 hours       | 6 hours     |
| Medium   | 6 hours       | 24 hours    |
| Low      | 12 hours      | 48 hours    |

> **Note:** The current v4.x defaults are different. See the Automations & SLA FAQ for up-to-date numbers.

## How are SLA timers calculated?

By default, SLA timers only count **business hours**. If your business hours are Monday–Friday, 9am–6pm, a ticket received at 5pm on Friday would have until 9am Monday before the timer starts counting toward a breach.

## What counts as a "first response"?

Only a **public reply** from an agent counts toward first response time. Internal notes do not stop the SLA timer.

## What should I do if an SLA is breached?

1. Review the escalation policy with your team lead.
2. Respond to the customer immediately with an apology and an ETA.
3. Flag the ticket with the `sla-breach` tag for reporting purposes.

## Can customers see SLA information?

No. SLA timers are internal. Customers see no indication of SLA status. Only agents and admins can view SLA details.
