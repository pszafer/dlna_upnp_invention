var fields;

function create_settings(server_name, ip_address, port, do_mimetype_container, transcoding, max_path){
	if (ip_address == 'None'){
		ip_address = '';
	}
	var gray = "enabled";
	if (ip_address == '' && server_name == '' && port == '' && do_mimetype_container == '' && transcoding == '' && max_path == ''){
		gray = "disabled";
	}
	fields = [
  		{ title: gettext('Name'), name: 'f_name', type: 'text', value: server_name, old_value:  server_name},
		{ title: gettext('IP Address'), name: 'f_ip', type: 'text', maxlen: 256,  value: ip_address, old_value: ip_address },
		{ title: gettext('Port'), name: 'f_port', type: 'text', maxlen: 256, value: port, old_value: port},
		{ title: gettext('Ignore patterns'), name: 'f_ignore', type: 'text', maxlen: 256, value: '', old_value: '' },
		{ title: gettext('Do mimetype containers'), name: 'f_mimetypecontainers', type: 'checkbox', value: (do_mimetype_container=='yes') ? "true" : "false", old_value: (do_mimetype_container=='yes') ? "true" : "false" },
		{ title: gettext('Transcoding'), name: 'f_transcoding', type: 'checkbox', value: (transcoding=='yes') ? "true" : "false"  , old_value: (transcoding=='yes') ? "true" : "false"   },
//		{ title: gettext('Icon'), name: 'f_icon', type: 'file', value: transcoding, old_value: (transcoding=='yes') ? "true" : "false"  },
		{ title: gettext('Max child items'), name: 'f_maxchild', type: 'text', value: max_path, old_value: max_path},
		]
	savetext = gettext('Save it');
	canceltext = gettext('Cancel');
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
					disabled: gray
				}).appendTo(td);
				break;
			case 'checkbox':
				if (field.value == 'yes'){
					jQuery('<input />', {
						id: field.name,
						type: field.type,
						checked : field.value,
						disabled: gray
					}).appendTo(td);
				}
				else {
					jQuery('<input />', {
						id: field.name,
						type: field.type,
						disabled: gray
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
					onclick: 'save_settings()',
					value: savetext,
					disabled: gray
				}).appendTo(td);
	tr = jQuery('<tr />', { }).appendTo(main_holder);
	td = jQuery('<td />', { 
		class: "tdbuttons",
		colspan: "2"
	}).appendTo(tr);
	jQuery('<input />', {
					id: 'cancel_button',
					type: 'button',
					value: canceltext,
					onclick: 'javascript:reloadPage();',
					disabled: gray
				}).appendTo(td);
}

function update_settings(server_name, ip_address, port, do_mimetype_container, transcoding, max_path){
	if (ip_address == 'None'){
		ip_address = '';
	}
	var gray = "enabled";
	if (ip_address == '' && server_name == '' && port == '' && do_mimetype_container == '' && transcoding == '' && max_path == ''){
		return;
	}
	fields = [
  		{ title: gettext('Name'), name: 'f_name', type: 'text', value: server_name, old_value:  server_name},
		{ title: gettext('IP Address'), name: 'f_ip', type: 'text', maxlen: 256,  value: ip_address, old_value: ip_address },
		{ title: gettext('Port'), name: 'f_port', type: 'text', maxlen: 256, value: port, old_value: port},
		{ title: gettext('Ignore patterns'), name: 'f_ignore', type: 'text', maxlen: 256, value: '', old_value: '' },
		{ title: gettext('Do mimetype containers'), name: 'f_mimetypecontainers', type: 'checkbox', value: (do_mimetype_container=='yes') ? "true" : "false", old_value: (do_mimetype_container=='yes') ? "true" : "false" },
		{ title: gettext('Transcoding'), name: 'f_transcoding', type: 'checkbox', value: (transcoding=='yes') ? "true" : "false", old_value: (transcoding=='yes') ? "true" : "false"   },
//		{ title: gettext('Icon'), name: 'f_icon', type: 'file', value: transcoding, old_value: (transcoding=='yes') ? "true" : "false"  },
		{ title: gettext('Max child items'), name: 'f_maxchild', type: 'text', value: max_path, old_value: max_path},
		]
	for (i=0; i<fields.length; ++i){
		field = fields[i];
		if (field.type == 'text'){
			$("#"+field.name).value = field.value;
		}
		else if (field.type == 'checkbox'){
			$('#'+field.name).checked = field.value;
		}
	}
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
			values[fields[i].name] = (check_val == "true") ? 'yes' : 'no';
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
		result = "0"
		$.ajax({
			url: "saveSettings",
			type: "POST",
			data:values,
			success: function(recv_data) {
				update_settings(recv_data['name'], recv_data['ip_addr'], recv_data['port'], recv_data['do_mimetype_container'], recv_data['transcoding'], recv_data['max_child_items']);
			},
			error: function(x,y,z) {
				result = "2";
			},
		});
	}
}