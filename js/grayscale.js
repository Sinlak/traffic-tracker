/*!
 * Start Bootstrap - Grayscale Bootstrap Theme (http://startbootstrap.com)
 * Code licensed under the Apache License v2.0.
 * For details, see http://www.apache.org/licenses/LICENSE-2.0.
 */

// jQuery to collapse the navbar on scroll
$(window).scroll(function() {
	if ($(".navbar").offset().top > 50) {
		$(".navbar-fixed-top").addClass("top-nav-collapse");
	} else {
		$(".navbar-fixed-top").removeClass("top-nav-collapse");
	}
});

// jQuery for page scrolling feature - requires jQuery Easing plugin
$(function() {
	$('#save-route').click(function() {
		$.post('/traffic/set_route', {
			addr1_from: "14300 Newport Ave",
			add2_from: "#81",
			city_from: "Tustin",
			state_from: "CA",
			addr1_from: "1073 N Batavia St",
			city_from: "Orange",
			state_from: "CA",

		}, function(data, textStatus) {
			alert(textStatus);
			if ('error' in data) {
				alert("<strong>Error!</strong> " + data.error);
				return;
			}
			alert(data.error);
			if (textStatus != 'success') {
				alert("<strong>Error!</strong> Unable to contact server", "err");
				return;
			}


			alert('<strong>Success!</strong> Processing has begun. Check the <b>Results</b> tab.', "success");
			upload();
		}).fail(function() {
			alert("<strong>Error!</strong> Unable to contact server", "err");
		}).always(function() {
			console.log("Done");
		});
	});
	$('a.page-scroll').bind('click', function(event) {
		var $anchor = $(this);
		$('html, body').stop().animate({
			scrollTop: $($anchor.attr('href')).offset().top
		}, 1500, 'easeInOutExpo');
		event.preventDefault();
	});
});

$(function() {
	$('#save-route').bind('click', function(event) {

	});
});


// Closes the Responsive Menu on Menu Item Click
$('.navbar-collapse ul li a').click(function() {
	$('.navbar-toggle:visible').click();
});
