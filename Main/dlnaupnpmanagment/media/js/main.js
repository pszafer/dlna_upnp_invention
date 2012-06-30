function createmenu(){
	var menu = [
	['Status',				'status'],
	['Settings',			'settings'],
	['Media',				'media'],
	['Log',					'logs'],
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

function reloadPage()
{
	document.location.reload(1);
}