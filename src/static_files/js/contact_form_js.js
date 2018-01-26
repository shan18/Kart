$(document).ready(function(){
	/* Contact Form Handler */
	
	var contactForm = $(".contact-form")
	var contactFormMethod = contactForm.attr("method")
	var contactFormEndpoint = contactForm.attr("action")

	function submitIndicator(submitButton, defaultText, doSubmit){
		if (doSubmit){
			submitButton.addClass("disabled")
			submitButton.html("<i class='fas fa-spinner fa-spin'></i>")
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
		submitIndicator(contactFormSubmitButton, "", true)
		$.ajax({
			method: contactFormMethod,
			url: contactFormEndpoint,
			data: contactFormData,
			success: function(data){
				thisForm[0].reset()
				$.alert({
					title: "Success!",
					content: data.message,
					theme: "modern"
				})

				setTimeout(function(){
					submitIndicator(contactFormSubmitButton, contactFormSubmitButtonText, false)
				}, 1500)
			},
			error: function(error){
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
					submitIndicator(contactFormSubmitButton, contactFormSubmitButtonText, false)
				}, 500)
			}
		})
	})
})