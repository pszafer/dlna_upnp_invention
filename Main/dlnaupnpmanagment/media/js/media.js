gettext('Save it');
gettext('Delete');
gettext('Cancel');
gettext("servernotrunning");
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
			value: gettext('Save it'),
			onClick: "save_item(\'"+name+"\',\'"+trname+"\')"
		}).appendTo(td);
		jQuery('<input />', {
			type: "button",
			value: gettext('Cancel'),
			onClick: "cancel_item(\'"+name+"\')"
		}).appendTo(td);
		
	}
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
		value: gettext('Delete'),
		class: "delete",
		onClick: "delete_item(this.id)"
	}).appendTo(td);
	
}