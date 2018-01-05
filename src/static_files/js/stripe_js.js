$(document).ready(function(){
	// Handling the stripe form module
	var stripeFormModule = $(".stripe-payment-form")
	var stripeModuleToken = stripeFormModule.attr("data-token")
	var stripeModuleNextUrl = stripeFormModule.attr("data-next-url")
	var stripeModuleBtnTitle = stripeFormModule.attr("data-btn-title") || "Add Card"

	var stripeTemplate = $.templates("#stripeTemplate")  // fetch the template
	var stripeTemplateContextData = {  // assign values to all variables in the template
		publishKey: stripeModuleToken,
		nextUrl: stripeModuleNextUrl,
		btnTitle: stripeModuleBtnTitle
	}
	// assign values to all the variables in the template
	var stripeTemplateHtml = stripeTemplate.render(stripeTemplateContextData)
	stripeFormModule.html(stripeTemplateHtml)

	// Processing the payment form
	var paymentForm = $(".payment-form")
	if (paymentForm.length > 1){
		alert("Only one payment form allowed per page!")
		paymentForm.css("display", "none")
	} else if (paymentForm.length == 1) {
		var pubKey = paymentForm.attr("data-token")
		var nextUrl = paymentForm.attr("data-next-url")
		var paymentFormButton = paymentForm.find(".payment-form-button")
		var paymentFormButtonText = paymentFormButton.text()

		// Create a Stripe client
		var stripe = Stripe(pubKey);

		// Create an instance of Elements
		var elements = stripe.elements();

		// Custom styling can be passed to options when creating an Element.
		// (Note that this demo uses a wider set of styles than the guide below.)
		var style = {
			base: {
				color: '#32325d',
				lineHeight: '18px',
				fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
				fontSmoothing: 'antialiased',
				fontSize: '16px',
				'::placeholder': {
					color: '#aab7c4'
				}
			},
			invalid: {
				color: '#fa755a',
				iconColor: '#fa755a'
			}
		};

		// Create an instance of the card Element
		var card = elements.create('card', {style: style});

		// Add an instance of the card Element into the `card-element` <div>
		card.mount('#card-element');

		// Handle real-time validation errors from the card Element.
		card.addEventListener('change', function(event) {
			var displayError = document.getElementById('card-errors');
			if (event.error) {
				displayError.textContent = event.error.message;
			} else {
				displayError.textContent = '';
			}
		});

		// Handle form submission
		var form = document.getElementById('payment-form');
		form.addEventListener('submit', function(event) {
			event.preventDefault();
			addPaymentIndicator(paymentFormButton, "", "Adding", true)

			stripe.createToken(card).then(function(result) {
				if (result.error) {
					// Inform the user if there was an error
					var errorElement = document.getElementById('card-errors');
					errorElement.textContent = result.error.message;
				} else {
					// Send the token to your server
					stripeTokenHandler(result.token, nextUrl);
				}
			});
		});

		function redirectToNext(nextPath, timeoffset){
			if (nextPath){
				setTimeout(function(){
					window.location.href = nextPath
				}, timeoffset)
			}
		}

		function addPaymentIndicator(submitButton, defaultText, submitText, doSubmit){
			if (doSubmit){
				submitButton.addClass("disabled")
				submitButton.html("<i class='fa fa-spin fa-spinner'></i> " + submitText + "...")
			} else {
				submitButton.removeClass("disabled")
				submitButton.html(defaultText)
			}
		}

		function stripeTokenHandler(token, nextUrl){
			var paymentMethodEndpoint = '/billing/payment-method/create/'
			var data = {
				'token': token.id
			}
			$.ajax({
				data: data,
				url: paymentMethodEndpoint,
				method: "POST",
				success: function(data){
					var successMsg = data.message || "Success! Your card was added."
					card.clear()  // Clears out form contents
					if (nextUrl){
						successMsg += "<br><br><i class='fa fa-spin fa-spinner'></i> Redirecting..."
					}
					if ($.alert){  // If the custom defined alert class exists
						$.alert(successMsg)
					} else {
						alert(successMsg)
					}
					redirectToNext(nextUrl, 1500)
					addPaymentIndicator(paymentFormButton, paymentFormButtonText, "", false)
				},
				error: function(error) {
					console.log(error)
					addPaymentIndicator(paymentFormButton, paymentFormButtonText, "", false)
				}
			})
		}
	}
})