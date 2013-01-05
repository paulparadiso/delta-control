var editorMode = 'name';
var currentPlaylistName = '';
var currentPlaylist = new Array();
var bRename = false;
var oldPlaylistName = '';
var highlightedCue = 0;
var bHaveHighlightedCue = false;
var playlistList = '';
var bHaveOpenPlaylist = false;

function init(){
	$.ajax({
		url:'getplaylists',
		type:'GET',
		success: function(data){
			playlistList = eval(data);
		}
	});
	$('.default').dropkick();
	//Cufon.replace('.hp-text');
}

function initDatepicker(){
	$(function() {
        $( "#datepicker" ).datepicker({
			onSelect: function(date){
				updateScheduler(date);
			}
		})
	});
}

function updateScheduler(date){
	$.ajax({
		url:'submitdate',
		type:'GET',
		data:{date:date},
		success: function(data){
			loadScheduler(data);
		}
	})
}

function loadScheduler(data){
	var playlists = eval('(' + data + ')');
	for(var p in playlists){
		if(playlists.hasOwnProperty(p)){
			var hour = "." + p.split(':')[0];
			var min = "." + p.split(':')[1];
			var playlist = playlists[p];
			$(hour + ' > ' + min).html(playlist);
		}
	}
}

function navClicked(nav){
	$('.')
}

function openPlaylistList(div){
	var listDiv = "#" + div;
	var plistDiv = listDiv + "-plist"
	var divState = $(listDiv).css('display');
	if(divState == 'none'){	
		if(bHaveOpenPlaylist){
			return;
		}
		$(listDiv).css('display','');
		var playlistHTML = '';
		for(var p in playlistList){
			playlistHTML += "<div onclick='setPlaylist(" 
							+ playlistList[p] + ", " 
							+ plistDiv +  ") " 
							+ "onmouseover='playlistHoverOn(" + plistDiv + ") " 
							+ "onmouseout='playlistHoverOff(" + plistDiv + ") " 
							+ "class='playlist-block'>" 
							+ playlistList[p] + "</div>";
		}
		$(listDiv).html(playlistHTML);
		bHaveOpenPlaylist = true;
	} else {
		$(listDiv).css('display','none');
		bHaveOpenPlaylist = false;
	}
}

function setPlaylist(plist, plistDiv){
	alert(plist);
}

function playlistHoverOn(plistDiv){
	$('#' + plistDiv).addClass('plist-item-hover');
}

function playlistHoverOff(plistDiv){
	$('#' + plistDiv).removeClass('plist-item-hover');
}

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

function swapPlaylistTab(currentTab){
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

function editClip(b){
	if(b == "true"){
		$('#clips-view').css('display','none');
		$('#clips-edit-view').css('display','');
		$('#new-clip-name').val("");
		$('#new-clip-ribbon').val("");
		$('#new-clip-concierge').val("");
	} else {
		loadClips();
		$('#clips-view').css('display','');
		$('#clips-edit-view').css('display','none')
	}
}

function saveClip(){
	var clipName = $('#new-clip-name').val();
	if(clipName == ''){
		alert("Please enter a name for the clip.");
		return;
	}
	var ribbonCue = $('#new-clip-ribbon').val();
	if(ribbonCue == ''){
		alert("Please enter a ribbon cue.")
		return;
	}
	var conciergeCue = $('#new-clip-concierge').val();
	if(conciergeCue == ''){
		alert("Please enter a concierge cue.")
		return;
	}
	$.ajax({
		url:'clips',
		type:'POST',
		data:{clipName:clipName,ribbonCue:ribbonCue,conciergeCue:conciergeCue},
		success:function(data){
			loadClips();
			editClip('false');
		}
	});
}

function loadClips(){
	$.ajax({
		url:'getclips',
		type:'GET',
		success:function(data){
			var cueList = JSON.parse(data);
			var cueHTML = "";
			//alert(cueList[]);
			for(var key in cueList){
				var markers = cueList[key].split(":");
				var cueName = key.split(":")[1];
				cueHTML += "<b>" + cueName + "</b>" + "<span style='float:right;'><img src='static/img/edit.png'></img></span><br>" +
				"<span style='margin-left:10px;'><b>Ribbon: </b>" + markers[0] + "</span><br>" +
				"<span style='margin-left:10px;'><b>Concierge: </b>" + markers[1] + "</span><br><br>";
			}
			$('#view-clips').html(cueHTML);
		}
	})
}

function swapClipsTab(currentTab){

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

function insertCue(cue){
	var cueDropdown = document.getElementById("cue-dropdown")
	var cue = cueDropdown.options[cueDropdown.selectedIndex].value;
	currentPlaylist.splice(parseInt(highlightedCue) + 1, 0, cue);
	currentPlaylist.join();
	deactivateHighlight();
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
		var cueId = "cue-" + cueIndex;
		playlistHTML += "<div onclick='toggleHighlight(" + i + ")' id='" + cueId + "' class='cue-item'>" + currentPlaylist[i] + 
		"</div><div onclick='removeCue(" + cueIndex + ")' class='cue-remove'><img src='static/img/remove.png'></img></div>"	;
	}
	$('#playlist-creator').html(playlistHTML);

}

function activateRenamePlaylist(){
	var name = $('#playlist-name-readout').html();
	alert("changing name of " + name);
	$('#playlist-name-readout').css('display','none');
	$('#playlist-name-input').css('display','');
	$('#playlist-name-rename').css('visibility','hidden');
	bRename = true;
}

function savePlaylist(){
	alert("saving playlist.");
	if(bRename){
		oldPlaylistName = currentPlaylistName;
		currentPlaylistName = document.getElementById('new-playlist-name').val();
		alert(currentPlaylistName);
	}
	$.ajax({
		url:'playlist',
		type:'POST',
		data:{name:currentPlaylistName,cmd:command}
	});
}

function cancelEdit(){
	swapTab('view');
}

function deactivateHighlight(){
	var cueId = "#cue-" + highlightedCue;
	$(cueId).removeClass('highlighted');
	bHaveHighlightedCue = false;
	$('#cue-insert').css('display','none');
	$('#cue-add').css('display','');
}

function toggleHighlight(cue){
	if(bHaveHighlightedCue == true){
		var bHighlight = false;
		var cueIndex = parseInt(cue);
		if(cueIndex != highlightedCue){
			bHighlight = true;
		}
		if(!bHighlight){
			deactivateHighlight();
		} else {
			var oldCueId = "#cue-" + parseInt(highlightedCue);
			var newCueId = "#cue-" + cueIndex;
			$(oldCueId).removeClass('highlighted');
			$(newCueId).addClass('highlighted');
			bHaveHighlightedCue = true;
			highlightedCue = cueIndex;
		}
	} else {
		var cueIndex = parseInt(cue);
		var cueId = "#cue-" + cue;
		$(cueId).addClass('highlighted');
		bHaveHighlightedCue = true;
		highlightedCue = cueIndex;
		$('#cue-add').css('display','none');
		$('#cue-insert').css('display','');
	}
}