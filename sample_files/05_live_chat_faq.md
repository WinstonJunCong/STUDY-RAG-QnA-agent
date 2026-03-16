# Live Chat — FAQ

## How do I add the live chat widget to my website?

After connecting Live Chat in **Settings → Channels → Live Chat**, you'll get a JavaScript snippet. Paste this inside the `<head>` tag of every page where you want the widget to appear.

```html
<script>
  window.NovaDesk = { key: "YOUR_WORKSPACE_KEY" };
</script>
<script src="https://cdn.novadesk.io/chat.js" async></script>
```

## Can I customize the chat widget's appearance?

Yes. Under **Settings → Live Chat → Widget Style** you can change:
- Widget color and button position (bottom-left or bottom-right)
- Greeting message
- Agent avatar
- Business hours visibility (shows "We're offline" when outside hours)

## Does the live chat widget work on mobile apps?

Yes. NovaDesk provides native SDKs for **iOS (Swift)** and **Android (Kotlin/Java)**. React Native and Flutter SDKs are available as community-supported packages.

## What happens to a chat when no agents are available?

If no agents are online, the widget automatically switches to **offline mode** and offers customers the option to leave a message, which gets converted into a ticket.

## Can customers start a chat without logging in?

Yes. Visitors can start an anonymous chat. If you want to identify customers, you can pass user attributes (name, email, user ID) to the widget using JavaScript:

```js
window.NovaDesk.identify({
  name: "Jane Doe",
  email: "jane@example.com",
  userId: "user_12345"
});
```

## Is chat history saved?

Yes. All chat transcripts are saved to the corresponding ticket in NovaDesk. Customers receive a copy of the transcript via email if they provide an address.

## What is the concurrent chat limit per agent?

By default, each agent can handle up to **5 simultaneous chats**. Admins can adjust this limit per agent under **Settings → Team → Agent Limits**.

## Does NovaDesk support chatbots?

NovaDesk has a built-in **AI Bot** (available on Growth and Enterprise plans) that can answer common questions from your knowledge base before routing to a human agent. You can also integrate third-party bots via the API.
