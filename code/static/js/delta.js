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
	oldTab = '';
	newTab = '';
	if(currentTab == 'view'){
		oldTab = '#edit-tab';
		newTab = '#view-tab';
	} else if(currentTab == 'edit'){
		oldTab = '#view-tab';
		newTab = '#edit-tab';
	}
	$(oldTab).removeClass('active-tab');
	$(oldTab).addClass('inactive-tab');
	$(newTab).removeClass('inactive-tab');
	$(newTab).addClass('active-tab');
}

function openPlaylist(plist){
	var plusSrc = 'static/img/plus.png';
	var minusSrc = 'static/img/minus.png';
	var plistImg = '#' + plist + ' img';
	var imgSrc = $(plistImg).first().attr('src');
	if(imgSrc == plusSrc){
		$(plistImg).first().attr('src', minusSrc);
	} else {
		$(plistImg).first().attr('src', plusSrc);
	}
}