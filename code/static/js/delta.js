var editorMode = 'name';
var currentPlaylistName = '';
var currentPlaylist = new Array();

function setCurrentPlaylistName(name){
	currentPlaylistName = name;
}

function addToCurrentPlaylist(item){
	currentPlaylist.push(item);
}

function clearCurrentPlaylist(){
	currentPlaylist = new Array();
}

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

function addCue(cue){
	var cueDropdown = document.getElementById("cue-dropdown")
	var cue = cueDropdown.options[cueDropdown.selectedIndex].value;
	currentPlaylist.push(cue);
	populatePlaylist();
}

function removeCue(cue){
	var cueIndex = parseInt(cue);
	currentPlaylist.splice(cueIndex,1);
	populatePlaylist();
} 

function populatePlaylist(){
	var playlistHTML = ''
	for(var i = 0; i < currentPlaylist.length; i++){
		var cueIndex = i.toString();
		playlistHTML += "<div class='cue-item'>" + currentPlaylist[i] + 
		"</div><div onclick='removeCue(" + cueIndex + ")' class='cue-remove'>x</div>"	;
	}
	$('#playlist-creator').html(playlistHTML);

}

function activateRenamePlaylist(){
	$('#playlist-name-readout').css('display','none');
	$('#playlist-name-input').css('display','');
	$('#playlist-name-rename').css('visibility','hidden');
}