$(document).ready(function(){

	/* Create new addresses */
	$(".new-address-card").click(function(event){
		window.location.href = "/address/create/"
	})

	/* Delete saved addresses */
	var addressDeleteLink = $(".delete-address")
	var addressDeleteForm = $(".delete-address-form")
	addressDeleteLink.click(function(event){
		event.preventDefault()
		var $this = $(this)
		addressDeleteForm.submit()
	})
})
