$(document).ready(function() {
	$('form').on('submit', function(event) {
		$.ajax({
			data : {
				human_players : $('#human_playersInput').val()
			},
			type : 'POST',
			url : '/process'
		})
		.done(function(data) {
			if (data.error) {
				$('#errorAlert').text(data.error).show();
				$('#successAlert').hide();
			}
			else {
				$('#successAlert').text(data.name).show();
				$('#errorAlert').hide();
			}
		});
		event.preventDefault();
	});
});