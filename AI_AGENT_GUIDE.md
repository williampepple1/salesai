# AI Agent Guide for Sellers

This guide explains how the AI sales agent works and how to get the best results.

## What the AI Agent Does

Your AI agent is a specialized sales assistant that:
- Operates 24/7 on Telegram
- Answers customer questions about YOUR products
- Shows product images and details
- Calculates prices with discounts
- Processes orders automatically
- Collects customer information

## Critical: Agent Boundaries

**The AI agent is programmed to ONLY discuss products in your catalog.**

### What This Means

✅ **The agent WILL:**
- Answer questions about your products
- Show product details, prices, and images
- Help customers make purchase decisions
- Process orders
- Explain your discounts

❌ **The agent WILL NOT:**
- Discuss products you don't sell
- Talk about politics, news, or current events
- Give general advice or information
- Engage in off-topic conversations
- Pretend to have products not in your catalog

## How It Stays Focused

The system uses multiple layers of protection:

1. **Strong Instructions**: The AI is explicitly told to only discuss your products
2. **Response Validation**: Every response is checked before being sent
3. **Automatic Redirection**: Off-topic attempts are replaced with product-focused responses
4. **Keyword Monitoring**: Detects and blocks common off-topic words

## Example Conversations

### Good Interaction

```
Customer: "Do you have laptops?"
Agent: "Yes! We have a high-performance laptop for $999.99. 
       It includes [features]. We currently have 5 in stock. 
       Would you like to know more?"

Customer: "How much for 2?"
Agent: "For 2 laptops, the total would be $1,999.98. 
       We also have a 10% discount when you buy 3 or more!"
```

### Off-Topic Protection

```
Customer: "What's the weather like?"
Agent: "I'm here specifically to help you with Test Store's products. 
       I can assist you with: Laptop, Mouse, Keyboard. 
       What would you like to know about our products?"

Customer: "Tell me about politics"
Agent: "I can only provide information about Test Store's products. 
       Is there anything about our Laptop, Mouse, or Keyboard 
       I can help you with?"
```

## Best Practices for Sellers

### 1. Write Clear Product Descriptions

The AI uses your product descriptions to answer questions:

✅ **Good**: "High-performance laptop with Intel i7, 16GB RAM, 512GB SSD, ideal for work and gaming"

❌ **Poor**: "Nice laptop"

### 2. Set Stock Levels Accurately

The agent checks stock before accepting orders:
- Keep stock quantities updated
- Mark products as unavailable when out of stock

### 3. Configure Discounts Properly

The agent automatically mentions discounts:
- Create clear discount rules (e.g., "10% off when buying 3+")
- Name rules descriptively (e.g., "Bulk discount" not "Rule 1")

### 4. Upload Quality Images

The agent sends product images to customers:
- Use clear, high-quality photos
- Show products from multiple angles
- Keep file sizes reasonable for fast loading

### 5. Monitor Conversations

Check the dashboard regularly to:
- Review customer conversations
- See what questions are being asked
- Identify products that need better descriptions
- Track orders and respond if needed

## Common Scenarios

### Scenario 1: Customer Asks About Unavailable Product

```
Customer: "Do you have blue shoes?"
Agent: "I can help you with our available products: 
       Laptop ($999.99), Mouse ($29.99), and Keyboard ($79.99). 
       Which one would you like to know more about?"
```

The agent won't make up products or promise items you don't have.

### Scenario 2: Customer Tries General Chat

```
Customer: "How are you today?"
Agent: "I'm here to help you with Test Store's products! 
       We have laptops, mice, and keyboards. 
       What can I help you find?"
```

The agent politely redirects to products.

### Scenario 3: Customer Asks Product Comparison

```
Customer: "Is your laptop better than Apple MacBook?"
Agent: "I can provide details about our high-performance laptop 
       at $999.99. It features Intel i7, 16GB RAM, and 512GB SSD. 
       Would you like to know more about its specifications?"
```

The agent focuses on YOUR products without comparing to competitors.

## Customizing the Experience

### Business Name

Set your business name in settings - the agent introduces itself using this name.

### Product Information

The more details you provide, the better the agent can help:
- Product name
- Detailed description
- Price
- Stock quantity
- Multiple images
- Category

### Discount Rules

Create discount rules to help drive sales:
- **Percentage**: "10% off when buying 3+"
- **Fixed**: "$20 off orders over $100"
- **Buy X Get Y**: "Buy 2 get 1 free"

The agent automatically mentions applicable discounts!

## Troubleshooting

### "Agent isn't mentioning my products"

**Check:**
- Products are marked as "Available"
- Products have stock quantity > 0
- Products have descriptions
- Bot token is configured correctly

### "Agent seems to go off-topic"

The system has multiple safeguards, but if you notice this:
1. Check the conversation logs
2. Report specific examples
3. The validation system should catch and correct this

### "Customers aren't completing orders"

**Common reasons:**
- Product out of stock
- Price seems unclear
- Discount not explained well
- Customer dropped off before providing address

**Solutions:**
- Keep stock updated
- Write clear descriptions
- Create attractive discounts
- Review conversation logs to see where customers stop

## Tips for Success

1. **Start Small**: Add 5-10 products first, test thoroughly
2. **Test Yourself**: Message your bot and try various scenarios
3. **Monitor Daily**: Check orders and conversations regularly
4. **Update Often**: Keep products, prices, and stock current
5. **Be Responsive**: While the bot handles most things, check for special requests

## Security & Privacy

- Customer data is stored securely
- Only you can access your dashboard
- Conversations are encrypted in transit
- The agent never shares customer data with other sellers
- Bot tokens are stored securely in AWS Secrets Manager

## Getting Help

If you need assistance:
1. Check conversation logs for patterns
2. Review product configurations
3. Test the bot yourself
4. Contact support if issues persist

## Advanced Features

### Custom Responses

While the agent is automated, you can:
- Review conversations
- Manually respond if needed
- See what customers are asking
- Adjust product info based on questions

### Analytics

Track performance:
- Number of conversations
- Orders placed
- Most asked-about products
- Conversion rate

### Scaling

As your business grows:
- Add more products
- Create more discount rules
- Monitor and optimize based on data

---

Remember: The AI agent is your 24/7 sales assistant that stays focused on YOUR products. It handles routine questions so you can focus on growing your business!
