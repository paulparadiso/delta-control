function sendCmd(cmdType, command){
	//alert(command + " pressed.");
	$.ajax({
		url:'control',
		type:'POST',
		data:{cmdtype:cmdType,cmd:command}
	});
}

function sendPlaylist(){
	var dd = document.getElementById("playlist-dropdown");
	var selectedPlaylist = dd.options[dd.selectedIndex].value;
	//alert(selectedPlaylist + " selected");
	sendCmd('playlist',selectedPlaylist);
}

function swapTab(currentTab){
	var oldTab = '';
	var newTab = '';
	var oldDiv = '';
	var newDiv = '';
	if(currentTab == 'view'){
		oldTab = '#edit-tab';
		newTab = '#view-tab';
		oldDiv = '#edit-view'
		newDiv = '#playlist-view'
	} else if(currentTab == 'edit'){
		oldTab = '#view-tab';
		newTab = '#edit-tab';
		oldDiv = '#playlist-view'
		newDiv = '#edit-view'
	}
	$(oldTab).removeClass('active-tab');
	$(oldTab).addClass('inactive-tab');
	$(oldDiv).css('display','none')
	$(newTab).removeClass('inactive-tab');
	$(newTab).addClass('active-tab');
	$(newDiv).css('display','');
}

function openPlaylist(plist){
	var plusSrc = 'static/img/plus.png';
	var minusSrc = 'static/img/minus.png';
	var plistImg = '#' + plist + ' img';
	var imgSrc = $(plistImg).first().attr('src');
	if(imgSrc == plusSrc){
		$(plistImg).first().attr('src', minusSrc);
		var cueDiv = '#' + plist + '-content';
		$(cueDiv).css('display','');
	} else {
		$(plistImg).first().attr('src', plusSrc);
		var cueDiv = '#' + plist + '-content';
		$(cueDiv).css('display','none');
	}
}