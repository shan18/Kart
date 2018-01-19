# Checkout Process

1. Cart -> Checkout View
	- Login/Register or Enter an Email (as Guest)
	- Shipping Address
	- Billing Info
		- Billing Address
		- Payment Method

2. Billing App/Component
	- Billing Profile
		- User or Email (Guest Email)
		- generate payment processor token (Stripe or Braintree)

3. Orders/Invoice Component
	- Connecting the Billing Profile
	- Shipping/Billing Address
	- Cart
	- Status -- Shipped? Cancelled?
