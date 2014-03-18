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
	
	
	//$('.table').tableAddCounter();
	$.getScript("http://code.jquery.com/ui/1.9.2/jquery-ui.js").done(function(script, textStatus) {
		//$('tbody').sortable();
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
		//pattern2 = /\D+/;
		text = text.split(pattern);
		//text += "\u00A0"
		
		//$("#playlist_option").tagit("createTag", text);
		
		//$("#playlist_option").hide()
		//document.getElementById("playlist_option").style.visibility = "hidden";
		console.log(text);
		
		playlist = text[0];
		//num = text[1];
		//num = num.split("");
		
		/*
		total = '';
		for (i = 0; i < num.length; i++){
			if ( (num[i] != "(") && (num[i] != ")") ){
				total = total + num[i]	
			}
		}
		
		//num = num[1]
		*/
		
		console.log(playlist);
		//console.log(total);
		//console.log(num);
		
		
		$("#playlist_option").data('tagit').tagInput.val(playlist);
		
		//var playlists = $("#playlist_option").val()
		//console.log("Playlist text is:" + playlists)
		//playlists += text
		//$("#playlist_option").val(playlists)
		//var temp = $("#playlist_option").val()
		//console.log("Playlist text is:" + temp)
	});	
	
	$("#playlist_option").tagit({
		allowSpaces: true
	});
	
	/*
	
	var app = angular.module("app", []);
	app.controller("AppCtrl", function(){
		var app = this;
		
		app.message = "Testing One Two One Two"
	});
	*/
	
	//$("#playlist_option").hide()
	//document.getElementById("playlist_option").style.visibility = "hidden";
	
	
	/*
	 function onYtEvent(payload) {
	 var logElement = document.getElementById('ytsubscribe-events-log');
	 if (payload.eventType == 'subscribe') {
	 logElement.innerHTML = 'You are subscribing to this channel'
	 } else if (payload.eventType == 'unsubscribe') {
	 logElement.innerHTML = 'You are unsubscribing from this channel'
	 }
	 if (window.console) {
	 	
	 window.console.log('ytsubscribe event: ', payload);
	 }
	 
	 
	 text += "\u00A0"
	 
	 }*/

});
/*
(function($) {
	$.fn.extend({
		tableAddCounter : function(options) {

			// set up default options
			var defaults = {
				title : '#',
				start : 1,
				id : false,
				cssClass : false
			};

			// Overwrite default options with user provided
			var options = $.extend({}, defaults, options);

			return $(this).each(function() {
				// Make sure this is a table tag
				if ($(this).is('table')) {

					// Add column title unless set to 'false'
					if (!options.title)
						options.title = '';
					$('th:first-child, thead td:first-child', this).each(function() {
						var tagName = $(this).prop('tagName');
						$(this).before('<' + tagName + ' rowspan="' + $('thead tr').length + '" class="' + options.cssClass + '" id="' + options.id + '">' + options.title + '</' + tagName + '>');
					});

					// Add counter starting counter from 'start'
					$('tbody td:first-child', this).each(function(i) {
						$(this).before('<td>' + (options.start + i) + '</td>');
					});

				}
			});
		}
	});
})(jQuery); 

*/