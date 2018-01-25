$(document).ready(function(){

	function checkoutFormIndicator(submitButton, text, doSubmit){
		if (doSubmit){
			submitButton.addClass("disabled")
			submitButton.html("<i class='fas fa-spinner fa-spin'></i> " + text + "...")
		} else {
			submitButton.removeClass("disabled")
			submitButton.html(text)
		}
	}

	var checkoutForm = $(".checkout-form")
	var checkoutFormMethod = checkoutForm.attr("method")
	var checkoutFormEndpoint = checkoutForm.attr("data-endpoint")

	checkoutForm.submit(function(event){
		event.preventDefault()
		var $this = $(this)
		var checkoutFormButton = $this.find("[type='submit']")
		var checkoutFormButtonText = checkoutFormButton.text()
		checkoutFormIndicator(checkoutFormButton, "Checking out", true)
		$.ajax({
			method: checkoutFormMethod,
			url: checkoutFormEndpoint,
			data: {},
			success: function(responseData){
				checkoutFormIndicator(checkoutFormButton, checkoutFormButtonText, false)
				window.location.href = responseData.next_path
			},
			error: function(error){
				$.alert("An error occured.")
				checkoutFormIndicator(checkoutFormButton, checkoutFormButtonText, false)
			}
		})
	})
})
