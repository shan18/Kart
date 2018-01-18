$(document).ready(function(){

	/* Cart + Add Products */
	var productForm = $(".form-product-ajax")

	function getOwnedProduct(productId, submitSpan) {
		var actionEndpoint = "/orders/endpoint/verify/ownership/"
		var httpMethod = "GET"
		var data = {
			product_id: productId
		}
		$.ajax({
			url: actionEndpoint,
			method: httpMethod,
			data: data,
			success: function(data){
				console.log(data)
				if(data.owner) {
					submitSpan.html("<a class='btn btn-warning' href='/library/'>In Library</a>")
				}
			},
			error: function(error){
				console.log(error)
			}
		})
	}

	$.each(productForm, function(index, object){  // loop through all the products in the view
		var $this = $(this)
		var isUser = $this.attr("data-user")
		var submitSpan = $this.find(".submit-span")
		var productInput = $this.find("[name='product_id']")
		var productId = productInput.attr("value")
		var productIsDigital = productInput.attr("data-is-digital")

		if(productIsDigital && isUser) {
			getOwnedProduct(productId, submitSpan)
		}
	})

	productForm.submit(function(event){
		event.preventDefault();
		var thisForm = $(this);
		// var actionEndpoint = thisForm.attr("action");
		var actionEndpoint = thisForm.attr("data-endpoint");  // See javascript_notes.txt
		var httpMethod = thisForm.attr("method");
		var formData = thisForm.serialize();

		$.ajax({
			url: actionEndpoint,
			method: httpMethod,
			data: formData,
			success: function(data){
				var submitSpan = thisForm.find(".submit-span")
				if (data.added) {
					submitSpan.html(
						"<div class='btn-group'><button type='submit' class='btn btn-danger'>" +
						"<i class='fa fa-shopping-cart' aria-hidden='true'></i> <i class='fa fa-times' aria-hidden='true'></i>" +
						"</button></div>"
					)
				} else {
					submitSpan.html("<button type='submit' class='btn btn-info'><i class='fa fa-cart-plus' aria-hidden='true'></i> <i class='fa fa-long-arrow-down' aria-hidden='true'></i></button>")
				}

				var cartItemCount = $(".cart-item-count")  // Refresh count in Navbar
				cartItemCount.text(data.cartItemCount)

				var currentPath = window.location.href      // Get current url
				if (currentPath.indexOf("cart") != -1) {    // If url contains 'cart'
					refreshCart()
				}
			},
			error: function(error){
				// Using '$.' uses jQuery-confirm instead of default
				$.alert({
					title: "Oops!",
					content: "An error may have occured!",
					theme: "modern"
				})
			}
		})
	})

	function refreshCart() {    // Refrest cart homepage if cart contents change
		console.log("In refresh method")
		var cartTable = $(".cart-table")
		var cartBody = cartTable.find(".cart-body")
		var productRow = cartBody.find(".cart-product")
		var currentUrl = window.location.href

		var refreshCartUrl = '/api/cart/'
		var refreshCartMethod = "GET"
		var data = {};
		$.ajax({
			url: refreshCartUrl,
			method: refreshCartMethod,
			data: data,
			success: function(data){
				var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
				if(data.products.length > 0) {
					productRow.html("")
					i = data.products.length
					$.each(data.products, function(index, value) {
						var newCartItemRemove = hiddenCartItemRemoveForm.clone()
						newCartItemRemove.css("display", "block")
						// newCartItemRemove.removeClass("hidden-class") // If class was used instead of style
						newCartItemRemove.find(".cart-item-product-id").val(value.id)
						cartBody.prepend("<tr><th scope=\"row\">" + i + "</th><td><a href='" + value.url + "'>" + value.name + "</a>" + newCartItemRemove.html() + "</td><td>" + value.price + "</td></tr>")
						i --
					})
					cartBody.find('.cart-subtotal').text(data.subtotal)
					cartBody.find('.cart-total').text(data.total)
				} else {
					window.location.href = currentUrl
				}
			},
			error: function(error){
				$.alert({
					title: "Oops!",
					content: "An error may have occured!",
					theme: "modern"
				})
			}
		})
	}

	/* Auto Search */
	var searchForm = $(".search-form")
	var searchInput = searchForm.find("[name='q']")   // input name = 'q'
	var typingInterval = 500  // in ms
	var typingTimer;
	var searchButton = searchForm.find("[type='submit']")

	searchInput.keyup(function(event){
		// key released
		// If the clearTimeout function is not used, then search begins after the specified time
		// starting from the time first keystroke was entered.
		clearTimeout(typingTimer)   // The timer is reset everytime something is entered in search bar
		typingTimer = setTimeout(performSearch, typingInterval)
	})

	searchInput.keydown(function(event){
		// key pressed
		clearTimeout(typingTimer)
	})

	function searchIndicator(){
		searchButton.addClass("disabled")
		searchButton.html("<i class='fa fa-spin fa-spinner'></i> Searching...")
	}

	function performSearch(){
		searchIndicator()
		var query = searchInput.val()
		setTimeout(function(){
			window.location.href = '/search/?q=' + query
		}, 1000)
	}

	/* Contact Form Handler */
	var contactForm = $(".contact-form")
	var contactFormMethod = contactForm.attr("method")
	var contactFormEndpoint = contactForm.attr("action")

	function submitIndicator(submitButton, defaultText, submitText, doSubmit){
		if (doSubmit){
			submitButton.addClass("disabled")
			submitButton.html("<i class='fa fa-spin fa-spinner'></i> " + submitText + "...")
		} else {
			submitButton.removeClass("disabled")
			submitButton.html(defaultText)
		}
	}

	// forms can be submitted by pressing Enter key too, This .submit function
	// handles that too, thus we use this instead of .click method.
	contactForm.submit(function(event){
		event.preventDefault()
		var contactFormSubmitButton = contactForm.find("[type='submit']")
		var contactFormSubmitButtonText = contactFormSubmitButton.text()
		var contactFormData = contactForm.serialize()
		var thisForm = $(this)
		submitIndicator(contactFormSubmitButton, "", "Sending", true)
		$.ajax({
			method: contactFormMethod,
			url: contactFormEndpoint,
			data: contactFormData,
			success: function(data){
				thisForm[0].reset()
				console.log(data)
				$.alert({
					title: "Success!",
					content: data.message,
					theme: "modern"
				})

				setTimeout(function(){
					submitIndicator(contactFormSubmitButton, contactFormSubmitButtonText, "", false)
				}, 1500)
			},
			error: function(error){
				console.log(error.responseJSON)
				var jsonData = error.responseJSON
				var message = ""

				// since it is a dictionary, we can use key & value in loop
				$.each(jsonData, function(key, value){
					message += key + ": " + value[0].message + "<br/>"
				})

				$.alert({
					title: "Oops!",
					content: message,
					theme: "modern"
				})

				setTimeout(function(){
					submitIndicator(contactFormSubmitButton, contactFormSubmitButtonText, "", false)
				}, 500)
			}
		})
	})
})