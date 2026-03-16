# Ticketing System — FAQ

## How does the ticketing system work?

Every inbound message from a connected channel (email, chat, social) automatically becomes a **ticket** in NovaDesk. Each ticket has a unique ID, a status, an assignee, and a priority level.

## What are the ticket statuses?

| Status       | Meaning                                          |
|--------------|--------------------------------------------------|
| Open         | Awaiting agent response                          |
| Pending      | Awaiting customer reply                          |
| On Hold      | Blocked — waiting on a third party               |
| Resolved     | Issue fixed; ticket closed after 72h of no reply |
| Closed       | Permanently closed; can be reopened              |

## Can customers reopen a closed ticket?

Yes. If a customer replies to a closed ticket's email thread within **30 days**, the ticket automatically reopens. After 30 days, a new ticket is created instead.

## What is ticket merging?

You can merge duplicate tickets from the same customer into a single conversation. Go to the ticket, click **⋯ More → Merge**, and search for the target ticket.

## How do I set ticket priority?

Priority can be set manually by an agent or automatically via Automation rules. The four levels are:

- 🔴 **Urgent** — SLA: respond within 1 hour
- 🟠 **High** — SLA: respond within 4 hours
- 🟡 **Medium** — SLA: respond within 8 hours
- 🟢 **Low** — SLA: respond within 24 hours

SLA timers only count **business hours** unless you configure 24/7 SLAs in Settings.

## Can I add private notes to a ticket?

Yes. Click **Add Note** inside a ticket to leave an internal comment visible only to agents. Notes are not sent to the customer.

## What are ticket tags?

Tags are free-form labels you can apply to tickets (e.g., `refund`, `bug`, `onboarding`). They're useful for filtering, reporting, and building automation rules.

## How many custom ticket fields can I create?

- Starter: up to 10 custom fields
- Growth: up to 50 custom fields
- Enterprise: unlimited custom fields

## Is there a ticket export feature?

Yes. Go to **Reports → Export** to download ticket data as CSV. Enterprise customers can also use the API for bulk exports.
