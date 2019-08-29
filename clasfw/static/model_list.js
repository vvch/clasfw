$(function() {
	/*
		Make amplitude table rows clickable
	*/
	$('TABLE.clickable TBODY TR').click(function() {
		var href = $(this).find('TD.hidden-link>A').attr('href')
		window.location = href
	})
});
