$(document).ready(function(){
	var addressDeleteLink = $(".delete-address")
	var addressDeleteForm = $(".delete-address-form")
	addressDeleteLink.click(function(event){
		event.preventDefault()
		var $this = $(this)
		addressDeleteForm.submit()
	})
})
