var fields;

function create_settings(server_name, ip_address, port, do_mimetype_container, transcoding){
	if (ip_address == 'None'){
		ip_address = '';
	}
	fields = [
  		{ title: 'Name', name: 'f_name', type: 'text', value: server_name, old_value:  server_name},
		{ title: 'IP Address', name: 'f_ip', type: 'text', maxlen: 256,  value: ip_address, old_value: ip_address },
		{ title: 'Port', name: 'f_port', type: 'text', maxlen: 256, value: port, old_value: port},
		{ title: 'Ignore patterns', name: 'f_ignore', type: 'text', maxlen: 256, value: '', old_value: '' },
		{ title: 'Do mimetype containers', name: 'f_mimetypecontainers', type: 'checkbox', value: do_mimetype_container, old_value: (do_mimetype_container=='yes') ? "true" : "false" },
		{ title: 'Transcoding', name: 'f_transcoding', type: 'checkbox', value: transcoding, old_value: (transcoding=='yes') ? "true" : "false"   },
		{ title: 'Icon', name: 'f_icon', type: 'checkbox', value: transcoding, old_value: (transcoding=='yes') ? "true" : "false"  },
		{ title: 'Max child items', name: 'f_maxchild', type: 'checkbox', value: transcoding, old_value: (transcoding=='yes') ? "true" : "false"   }
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
					id: field.name,
					type: field.type,
					maxlength: field.maxlen,
					value: field.value,
				}).appendTo(td);
				break;
			case 'checkbox':
				if (field.value == 'yes'){
					jQuery('<input />', {
						id: field.name,
						type: field.type,
						checked : field.value
					}).appendTo(td);
				}
				else {
					jQuery('<input />', {
						id: field.name,
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
					onclick: 'save_settings()'
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

function save_settings(){
	var values = {};
	changed = false;
	for (i=0; i<fields.length; ++i){
		if ($("#"+fields[i].name).is(':checkbox')){
			check_val = $("#"+fields[i].name).is(':checked').toString();
			if (fields[i].old_value != check_val){
				changed = true;
			}
			values[fields[i].name] = (check_val)? 'yes' : 'no';
		}
		else {
			new_value = $("#"+fields[i].name).val();
			if (new_value != fields[i].old_value){
				changed = true;
			}
			values[fields[i].name] = new_value;
		}
	}
	if (changed == true){
		$.ajax({
			url: "saveSettings",
			type: "POST",
			data:values,
			success: function(data) {
				alert("hej");
			},
			error: function(x,y,z) {
				result = false;
			},
		});
	}
}