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

		// Handle form submission (using javascript)
		// var form = document.getElementById('payment-form');
		// form.addEventListener('submit', function(event) {
		// 	event.preventDefault();

		// 	var loadTime = 1500
		// 	var errorHtml = "<i class='fas fa-exclamation-circle'></i> An error occured"
		// 	var errorClasses = "btn btn-danger disable my-3"
		// 	var loadingHtml = "<t class='fas fa-spinner fa-spin'></i> Loading..."
		// 	var loadingClasses = "btn btn-success disable my-3"

		// 	stripe.createToken(card).then(function(result) {
		// 		if (result.error) {
		// 			// Inform the user if there was an error
		// 			var errorElement = document.getElementById('card-errors');
		// 			errorElement.textContent = result.error.message;
		// 		} else {
		// 			// Send the token to your server
		// 			stripeTokenHandler(result.token, nextUrl);
		// 		}
		// 	});
		// });

		var form = $('#payment-form');
		var formButton = form.find(".payment-form-button")
		var formButtonDefaultHtml = formButton.html()
		var formButtonDefaultClasses = formButton.attr("class")
		
		 // this is taken because of displayBtnStatus function we added below outside the else block
		var formButtonPreviousClasses = formButtonDefaultClasses

		// Handle form submission (using jQuery)
		form.on('submit', function(event) {
			event.preventDefault();

			formButton.blur()  // remove focus around the button
			/* We could have called the success displayBtnStatus in the else block below, but
				 in a slow internet connection, the flow takes time to reach there and hence
				 a lag is visible, so we add it here.
			*/
			displayBtnStatus(
				formButton,
				"<i class='fas fa-spinner fa-spin disable'></i> Adding...",
				"btn btn-success my-3",
				false
			)

			stripe.createToken(card).then(function(result) {
				if (result.error) {
					// Inform the user if there was an error
					var errorElement = $('#card-errors');
					errorElement.textContent = result.error.message;
					displayBtnStatus(
						formButton,
						"<i class='fas fa-exclamation-circle disable'></i> An error occured",
						"btn btn-danger my-3",
						true
					)
				} else {
					// Send the token to your server
					stripeTokenHandler(result.token, nextUrl);
				}
			});
		});

		function displayBtnStatus(element, newHtml, newClasses, doTimeout){
			element.html(newHtml)
			element.removeClass(formButtonPreviousClasses)
			element.addClass(newClasses)
			formButtonPreviousClasses = newClasses
			if (doTimeout) {
				setTimeout(function(){
					element.html(formButtonDefaultHtml)
					element.removeClass(formButtonPreviousClasses)
					element.addClass(formButtonDefaultClasses)
				}, 1000)
			}
		}

		function redirectToNext(nextPath, timeoffset){
			if (nextPath){
				setTimeout(function(){
					window.location.href = nextPath
				}, timeoffset)
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
						successMsg += "<br><br><i class='fas fa-spinner fa-spin'></i> Redirecting..."
					}
					if ($.alert){  // If the custom defined alert class exists
						$.alert(successMsg)
					} else {
						alert(successMsg)
					}
					formButton.html(formButtonDefaultHtml)
					formButton.attr('class', formButtonDefaultClasses)
					redirectToNext(nextUrl, 1500)
				},
				error: function(error) {
					if ($.alert){  // If the custom defined alert class exists
						$.alert({title: "An error occured", content: "Please try adding your card again."})
					} else {
						alert("Error! Please try adding your card again.")
					}
					formButton.html(formButtonDefaultHtml)
					formButton.attr('class', formButtonDefaultClasses)
				}
			})
		}
	}
})