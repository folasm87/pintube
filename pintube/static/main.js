$(document).ready(function() {
	$('.collapse').on('show.bs.collapse', function() {
		var id = $(this).attr('id');
		$('a[href="#' + id + '"]').closest('.panel-heading').addClass('active-faq');
		$('a[href="#' + id + '"] .panel-title span').html('<i class="glyphicon glyphicon-minus"></i>');
	});
	$('.collapse').on('hide.bs.collapse', function() {
		var id = $(this).attr('id');
		$('a[href="#' + id + '"]').closest('.panel-heading').removeClass('active-faq');
		$('a[href="#' + id + '"] .panel-title span').html('<i class="glyphicon glyphicon-plus"></i>');
	});
	
	
	$.getScript("http://code.jquery.com/ui/1.9.2/jquery-ui.js").done(function(script, textStatus) {
		$(".alert-info").alert('close');
		$(".alert-success").show();
	});
	

	$(".modal-wide").on("show.bs.modal", function() {
		var height = $(window).height() - 200;
		$(this).find(".modal-body").css("max-height", height);
	});
	
	
	$("#playlist-add li a").click(function(){
		var text = $(this).text();
		pattern = /(\(\d+\))/;
		text = text.split(pattern);
		playlist = text[0];
		$("#playlist_option").data('tagit').tagInput.val(playlist);
	});	
	
	$("#playlist_option").tagit({
		allowSpaces: true
	});

});