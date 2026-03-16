# Integrations & API — FAQ

## What integrations does NovaDesk support?

NovaDesk offers native integrations with:

| Category        | Tools                                          |
|-----------------|------------------------------------------------|
| CRM             | Salesforce, HubSpot, Pipedrive, Zoho CRM       |
| E-commerce      | Shopify, WooCommerce, Magento                  |
| Communication   | Slack, Microsoft Teams                         |
| Project Mgmt    | Jira, Linear, Asana, Trello                    |
| Analytics       | Google Analytics, Segment, Mixpanel            |
| Billing         | Stripe, Chargebee, Recurly                     |

Additional integrations are available via Zapier and Make (formerly Integromat).

## How do I connect Slack to NovaDesk?

1. Go to **Settings → Integrations → Slack**.
2. Click **Connect** and authenticate with your Slack workspace.
3. Choose which channels receive new ticket notifications and configure the notification triggers.

Once connected, agents can reply to tickets directly from Slack.

## Does NovaDesk have a public API?

Yes. NovaDesk provides a RESTful API documented at [docs.novadesk.io/api](https://docs.novadesk.io/api). The API supports:
- Creating, updating, and closing tickets
- Managing contacts and companies
- Retrieving reports and metrics
- Webhooks for real-time event notifications

## How do I get an API key?

Go to **Settings → Developer → API Keys** and click **Generate Key**. Keep your key secret — it grants full access to your account data.

## What are the API rate limits?

| Plan       | Rate Limit               |
|------------|--------------------------|
| Starter    | 100 requests/minute      |
| Growth     | 500 requests/minute      |
| Enterprise | Custom (contact support) |

Exceeding the rate limit returns an HTTP `429 Too Many Requests` response.

## Can I use webhooks?

Yes. Configure webhooks under **Settings → Developer → Webhooks**. You can subscribe to events such as:
- `ticket.created`
- `ticket.assigned`
- `ticket.resolved`
- `message.received`
- `contact.created`

Webhooks are sent as HTTP POST requests with a JSON payload and an HMAC-SHA256 signature for verification.

## Is there an official SDK?

Official SDKs are available for **Node.js** and **Python**. Community SDKs exist for Ruby, PHP, and Go. Find them at [github.com/novadesk](https://github.com/novadesk).
