function createmenu(){
	var menu = [
	['Status',				'status'],
	['Settings',			'settings'],
	['Media',				'media'],
	['Help',				'help'],
	];
	var content = [];
	for (i = 0; i< menu.length; ++i){
		var item = menu[i];
		if (!item){
			// jQuery('<br />').appendTo('#menu');
			content.push('<br />');
		}
		if (item.length == 2){
			jQuery('<a/>', {
			    class: 'indent1',
			    href: item[1],
			    title: item[0],
			    text: item[0]
			}).appendTo('#menu');
		}
	}
}

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
				text: "No UUID"
			}).appendTo(main_holder);
		}
	});
}

function clean_container(container){
	// container = $(name);
	container
}

function update(){
	update_holder = $("#update-holder");
	if (update_holder.length == 0){
		main_holder = $("#main-holder");
		update_holder = jQuery('<div/>',{
			id: 'update-holder'
		}).appendTo(main_holder);
	}
	
	most_recent = update_holder.find("div:first");
	$.getJSON("update", function(data){
		cycle_class = most_recent.hasClass('odd') ? "even" : "odd";
		id = parseInt(most_recent.attr('id'))
		if (isNaN(id)){
			id = 0
		}
		else {
			id += 1;
		}
		jQuery.each(data, function() {
					// alert(cycle_class);
					some_string = '<div id="'+id+'" class="update ' + cycle_class
						+ '"><div class="timestamp">'
						+ this.fields.timestamp
						+ '</div><div class="text">'
						+ this.fields.body + " " + id
						+ '</div><div class="clear"></div></div>';
					// alert(some_string);
					update_holder.prepend(some_string);
				cycle_class = (cycle_class == "odd")? "even" : "odd";
				});
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
	$("#status").empty();
	$.ajax({
		url: "serverstatus",
		success: function(data) {
			stat = data.Status;
			if (stat == 'Failed'){
				jQuery('<p/>', {
					style: "color: red;",
					text: 'down' 
				}).appendTo("#status");
				managing_server_status = false;
			}
			else if (stat == 'Running') {
				jQuery('<p/>', {
					style: "color: green;",
					text: 'running' 
				}).appendTo("#status");
				managing_server_status = true;
			}
		},
		error: function(x,y,z) {
			jQuery('<p/>', {
					style: "color: red;",
					text: 'down' 
				}).appendTo("#status");
			managing_server_status = false;
		}
	});
}

function get_upnp_server_status(){
	$("#status2").empty();
	$.ajax({
		url: "upnpserverstatus",
		success: function(data) {
			stat = data.Status;
			if (stat == 'Failed'){
				jQuery('<p/>', {
					style: "color: red;",
					text: 'down' 
				}).appendTo("#status2");
			}
			else if (stat == 'Running'){
				jQuery('<p/>', {
					style: "color: green;",
					text: 'running' 
				}).appendTo("#status2");
			}
		},
		error: function(x,y,z) {
			jQuery('<p/>', {
					style: "color: red;",
					text: 'down' 
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

function reloadPage()
{
	document.location.reload(1);
}

function create_settings(server_name, ip_address, port, do_mimetype_container, transcoding){
	if (ip_address == 'None'){
		ip_address = '';
	}
	fields = [
		{ title: 'Name', name: 'f_name', type: 'text', value: server_name },
		{ title: 'IP Address', name: 'f_ip', type: 'text', maxlen: 256,  value: ip_address },
		{ title: 'Port', name: 'f_port', type: 'text', maxlen: 256, value: port},
		{ title: 'Ignore patterns', name: 'f_ignore', type: 'text', maxlen: 256, value: '' },
		{ title: 'Do mimetype containers', name: 'f_mimetypecontainers', type: 'checkbox', value: do_mimetype_container },
		{ title: 'Transcoding', name: 'f_transcoding', type: 'checkbox', value: transcoding },
		{ title: 'Icon', name: 'f_transcoding', type: 'checkbox', value: transcoding },
		{ title: 'Max child items', name: 'f_transcoding', type: 'checkbox', value: transcoding }
		]
	main_holder = $("#savecancel-table");
	main_holder.empty();
	for (i=0; i<fields.length; ++i){
		field = fields[i];
		tr = jQuery('<tr />', { }).appendTo(main_holder);
		td = jQuery('<td />', { }).appendTo(tr);
		td.append('<p>'+field.title+'</p>');
		td = jQuery('<td />', { }).appendTo(tr);
		switch (field.type){
			case 'text':
				jQuery('<input />', {
					name: field.name,
					type: field.type,
					maxlength: field.maxlen,
					value: field.value,
				}).appendTo(td);
				break;
			case 'checkbox':
				if (field.value == 'yes'){
					jQuery('<input />', {
						name: field.name,
						type: field.type,
						checked : field.value
					}).appendTo(td);
				}
				else {
					jQuery('<input />', {
						name: field.name,
						type: field.type
					}).appendTo(td);
				}
				break;
		}
	}
	tr = jQuery('<tr />', { }).appendTo(main_holder);
	td = jQuery('<td />', { }).appendTo(tr);
	td.append('<p>&nbsp;</p>');
	tr = jQuery('<tr />', { }).appendTo(main_holder);
	td = jQuery('<td />', { 
		class: "tdbuttons",
		colspan: "2"
	}).appendTo(tr);
	jQuery('<input />', {
					id: 'save_button',
					type: 'button',
					value: 'Save',
					onclick: 'save()'
				}).appendTo(td);
	tr = jQuery('<tr />', { }).appendTo(main_holder);
	td = jQuery('<td />', { 
		class: "tdbuttons",
		colspan: "2"
	}).appendTo(tr);
	jQuery('<input />', {
					id: 'cancel_button',
					type: 'button',
					value: 'Cancel',
					onclick: 'javascript:reloadPage();'
				}).appendTo(td);
}

function create_single_content_item(main_holder, id, name, type, value){
	tr = jQuery('<tr />', { 
		id:"row"+id
		}).appendTo(main_holder);
	td = jQuery('<td />', {
	}).appendTo(tr);
	//td.append('<p>'+field.title+'</p>');
	jQuery('<input />', {
		name: name,
		type: type,
		value: value,
	}).appendTo(td);
	td = jQuery('<td />', {}).appendTo(tr);
	jQuery('<input />', {
		id: id,
		type: "button",
		value: "Delete",
		class: "delete",
		onClick: "delete_item(this.id)"
	}).appendTo(td);
	
}

function empty_rows_content_table(main_holder, row_id){
	tr = jQuery('<tr />', {
		id: row_id
		}).appendTo(main_holder);
	td = jQuery('<td />', { }).appendTo(tr);
	td.append('<p>&nbsp;</p>');
	
	tr = jQuery('<tr />', { }).appendTo(main_holder);
	td = jQuery('<td />', { }).appendTo(tr);
	td.append('<p>&nbsp;</p>');
}

function create_content_table(pathlist){
	fields = []
	for (object in pathlist){
		array = new Array()
		array.type = 'text';
		array.name = 'f_path';
		array.value = object.path;
		array.id = object.id;
		fields.add(array);
	}
	main_holder = $("#status-table");
	main_holder.empty();
	for (i=0; i<fields.length; ++i){
		field = fields[i];
		create_single_content_item(main_holder, field.id, field.name, field.type, field.value);
	}
	finish_content_table(main_holder);
	
}

function delete_item(id){
	$("#row"+id).remove();
}

function add_content_row(){
	if ($("#new_content_row").length <= 0){
		main_holder = $("#last_row");
		name = "new_content_row";
		trname = "new_content_text"
		tr = jQuery('<tr />', { 
			id:name
			});
		main_holder.after(tr);
		td = jQuery('<td />', {
		}).appendTo(tr);
		//td.append('<p>'+field.title+'</p>');
		jQuery('<input />', {
			id: trname,
			type: "text",
		}).appendTo(td);
		td = jQuery('<td />', {}).appendTo(tr);
		jQuery('<input />', {
			type: "button",
			value: "Save it",
			onClick: "save_item(\'"+name+"\',\'"+trname+"\')"
		}).appendTo(td);
		jQuery('<input />', {
			type: "button",
			value: "Cancel",
			onClick: "cancel_item(\'"+name+"\')"
		}).appendTo(td);
		
	}
}

function cancel_item(id){
	$("#"+id).remove();
}

function save_item(row, trobject){
	text = $("#"+trobject).val();
	$.ajax({
		url: "addContent",
		type: "POST",
		data:{
			content: text
		},
		success: function(data) {
			alert("hej");
		},
		error: function(x,y,z) {
			result = false;
		},
	});
}