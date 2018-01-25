$(document).ready(function(){
	/* Auto Search */

	function searchIndicator(){
		searchButton.addClass("disabled")
		searchButton.html("<i class='fas fa-spinner fa-spin'></i>")
	}

	function performSearch(){
		searchIndicator()
		var query = searchInput.val()
		setTimeout(function(){
			window.location.href = '/search/?q=' + query
		}, 1000)
	}
	
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
})