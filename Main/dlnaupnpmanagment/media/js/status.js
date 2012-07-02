function server_start(){
	$.ajax({
		url: "runserver",
		success: function(data) {
			alert("test");
			setTimeout(function(){
			$.ajax({
				url: "checkAddress",
				success: function(data) {
					alert("ok");
				},
				error: function(x,y,z) {
					alert("error2");
				}
			});
			get_all_status();
			}, 100);					
		},
		error: function(x,y,z) {
			alert("error");
		}
	});
}

function stop_server(){
	$.ajax({
		url: "stopserver",
		success: function(data) {
			setTimeout(function(){
			$.ajax({
				url: "checkAddress",
				success: function(data) {
					alert("ok");
				},
				error: function(x,y,z) {
					alert("error");
				}
			});
			get_all_status();
			}, 1000);					
		},
		error: function(x,y,z) {
			alert("error");
		}
	});
}

function getuuid(){
	$.ajax({
		url: "getuuid",
		success: function(data) {
			main_holder = $("#uuidtd");
			jQuery('<div/>',{
				class: "update even",
				text: data.UUID
			}).appendTo(main_holder);
		},
		error: function(x,y,z) {
			main_holder = $("#uuidtd");
			jQuery('<div/>',{
				class: "update even",
				text: gettext("No UUID")
			}).appendTo(main_holder);
		}
	});
}

var managing_server_working = false;

function get_all_status(){
	get_server_status4statuspage();
	get_upnp_server_status();
}

function check_address(){
	$.ajax({
		url: "checkAddress",
		success: function(data) {
			get_upnp_server_status()
		},
		error: function(x,y,z) {
			return;
		}
	});
}

function get_server_status4statuspage(){
	element = $("#status");
	current_state = element.text();
	$.ajax({
		url: "serverstatus",
		success: function(data) {
			stat = data.Status;
			if (stat == 'Failed' && current_state != gettext("down")){
				$("#status").empty();
				jQuery('<p/>', {
					id: 'p_stat',
					style: "color: red;",
					text: gettext('down') 
				}).appendTo("#status");
				managing_server_status = false;
			}
			else if (stat == 'Running' && current_state != gettext('running')){
				$("#status").empty();
				jQuery('<p/>', {
					id: 'p_stat',
					style: "color: green;",
					text: gettext('running') 
				}).appendTo("#status");
				managing_server_status = true;
			}
		},
		error: function(x,y,z) {
			$("#status").empty();
			jQuery('<p/>', {
					id: 'p_stat',
					style: "color: red;",
					text: gettext('down') 
				}).appendTo("#status");
			managing_server_status = false;
		}
	});
}

function get_upnp_server_status(){
	element = $("#status2");
	current_state = element.text();
	$.ajax({
		url: "upnpserverstatus",
		success: function(data) {
			stat = data.Status;
			if (stat == 'Failed'  && current_state != gettext('down')){
				$("#status2").empty();
				jQuery('<p/>', {
					id: 'p_stat2',
					style: "color: red;",
					text: gettext('down') 
				}).appendTo("#status2");
			}
			else if (stat == 'Running' && current_state != gettext('running')){
				$("#status2").empty();
				jQuery('<p/>', {
					id: 'p_stat2',
					style: "color: green;",
					text: gettext('running')
				}).appendTo("#status2");
			}
		},
		error: function(x,y,z) {
			$("#status2").empty();
			jQuery('<p/>', {
				id: 'p_stat2',
				style: "color: red;",
				text: gettext('down') 
			}).appendTo("#status2");
		}
	});
}

function get_server_status(asynchronous){
	var result = false;
	if (asynchronous == null){
		asynchronous = true;
	}
	$.ajax({
		url: "serverstatus",
		async: asynchronous,
		success: function(data) {
			stat = data.Status;
			if (stat == 'Failed'){
				result = false;
			}
			else if (stat == 'Running') {
				result = true;
			}
		},
		error: function(x,y,z) {
			result = false;
		},
	});
	return result;
}