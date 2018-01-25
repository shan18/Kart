$(document).ready(function(){

	function accountFormIndicator(submitButton, text, doSubmit){
		if (doSubmit){
			submitButton.addClass("disabled")
			submitButton.html("<i class='fas fa-spinner fa-spin'></i> " + text + "...")
		} else {
			submitButton.removeClass("disabled")
			submitButton.html(text)
		}
	}

	var accountForm = $(".account-form")
	var accountFormMethod = accountForm.attr("method")
	var accountFormEndpoint = accountForm.attr("data-endpoint")

	accountForm.submit(function(event){
		event.preventDefault()
		var $this = $(this)
		var accountFormButton = $this.find("[type='submit']")
		var accountFormButtonText = accountFormButton.text()
		var accountFormData = $this.serialize()
		accountFormIndicator(accountFormButton, "Submitting", true)
		$.ajax({
			method: accountFormMethod,
			url: accountFormEndpoint,
			data: accountFormData,
			success: function(responseData){
				if (responseData.success){
					accountFormIndicator(accountFormButton, accountFormButtonText, false)
					window.location.href = responseData.next_path
				} else {
					setTimeout(function(){
						accountFormIndicator(accountFormButton, accountFormButtonText, false)
						window.location.href = responseData.next_path
					}, 300)
				}
			},
			error: function(error){
				$.alert("An error occured.")
				setTimeout(function(){
					accountFormIndicator(accountFormButton, accountFormButtonText, false)
					if (error.next_path){
						window.location.href = error.next_path
					}
				}, 300)
			}
		})
	})
})
