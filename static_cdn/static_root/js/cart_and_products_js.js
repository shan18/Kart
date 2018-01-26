$(document).ready(function(){

	/* Products List Sort */
	$(document).ready(function(){
		var formB = $(".sort-btn")
		formB.hover(
			function(){
				var $this = $(this)
				$this.addClass('sort-hover');
			},
			function(){
				var $this = $(this)
				$this.removeClass('sort-hover');
			}
		)
	})


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
				if (data.noLoginDigital){
					$.confirm({
						icon: 'fas fa-sign-in-alt',
						title: 'Login Required',
						content: 'You must login, in order to purchase any digital items!',
						type: 'dark',
    					typeAnimated: true,
						buttons: {
							login: {
								text: 'Login',
								action: function () {
									window.location.href = '/login/'
								}
							},
							list: {
								text: 'Continue as guest'
							}
						}
					});
				} else {
					var submitSpan = thisForm.find(".submit-span")
					if (data.added) {
						submitSpan.html(
							"<div class='btn-group'><button type='submit' class='btn btn-danger'>" +
							"<i class='fas fa-shopping-cart' aria-hidden='true'></i> " +
							"<i class='fas fa-times' aria-hidden='true'></i>" +
							"</button></div>"
						)
					} else {
						submitSpan.html(
							"<button type='submit' class='btn btn-info'>" +
							"<i class='fas fa-cart-plus' aria-hidden='true'></i> " +
							"<i class='fas fa-long-arrow-alt-down' aria-hidden='true'></i>" +
							"</button>"
						)
					}

					var cartItemCount = $(".cart-item-count")  // Refresh count in Navbar
					cartItemCount.text(data.cartItemCount)

					var currentPath = window.location.href      // Get current url
					if (currentPath.indexOf("cart") != -1) {    // If url contains 'cart'
						refreshCart()
					}
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
						cartBody.prepend(
							"<tr><th scope=\"row\">" + i + "</th><td><a href='" +
							value.url + "'>" + value.name + "</a>" + newCartItemRemove.html() + "</td><td>" +
							value.price + "</td></tr>"
						)
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
})