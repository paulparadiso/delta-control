var editorMode = 'name';
var currentPlaylistName = '';
var currentPlaylist = new Array();
var bRename = false;
var oldPlaylistName = '';
var highlightedCue = 0;
var bHaveHighlightedCue = false;
var playlistList = '';
var bHaveOpenPlaylist = false;
var clipList;
var bEditingClip = false;
var editedClip;

function init(){
	$.ajax({
		url:'getplaylists',
		type:'GET',
		success: function(data){
			playlistList = eval(data);
		}
	});
	//$('.default').dropkick();
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

function resetScheduler(){
	for(var i = 0; i < 24; i++){
		for(var j = 0; j < 60; j += 15){
			var ddId = "#dd-" + i.toString() + "-" + j.toString();
			$(ddId).val("none");
		}
	}
}

function loadScheduler(data){
	var playlists = eval('(' + data + ')');
	resetScheduler(); 
	for(var p in playlists){
		if(playlists.hasOwnProperty(p)){
			var hour = p.split(':')[0];
			var min = p.split(':')[1];
			if(min == "00"){
				min = "0";
			}
			var ddId = "#dd-" + hour + "-" + min;
			var playlist = playlists[p];
			//alert("setting " + ddId + " to " + playlist);
			//$(hour + ' > ' + min).html(playlist);
			$(ddId).val(playlist);
		}
	}
}

function getSchedule(){
	var date = $('#datepicker').val();
	if(date == ""){
		alert("No date selected.");
		return;
	}
	var data = new Object;
	for(var i = 0; i < 24; i++){
		for(var j = 0; j < 60; j += 15){
			var dropdown = "#dd-" + i.toString() + "-" + j.toString();
			var dropdownVal = $(dropdown).val();
			if(dropdownVal != ""){
				//alert(dropdown + " = " + dropdownVal);
				data[i.toString() + ':' + j.toString()] = dropdownVal;
			}
		}
	}
	/*
	if(!$.isEmptyObject(data)){
		data['date'] = date;
		return data;
	} else {
		return false;
	}
	*/
	//Need to send empty schedule in order to reset dates.
	data['date'] = date;
	return data;
}

function saveSchedule(mode){
	var schedule = getSchedule();
	if(schedule){
		schedule["mode"] = mode;
		$.ajax({
			url:'submitschedule',
			type:'POST',
			data:schedule,
			success:function(data){
				alert("Schedule successfully saved.")
			}
		});
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

function getPlaylist(plist){
	$.ajax({
		url:'getplaylist',
		type:'GET',
		data:{playlist:plist},
		success:function(data){
			currentPlaylist = JSON.parse(data);
			currentPlaylistName = plist;
			populatePlaylist();
		}
	})
}

function editPlaylist(plist){
	getPlaylist(plist);
	oldTab = '#view-tab';
	newTab = '#edit-tab';
	oldDiv = '#playlist-view'
	newDiv = '#edit-view'
	$(oldTab).removeClass('active-tab');
	$(oldTab).addClass('inactive-tab');
	$(oldDiv).css('display','none')
	$(newTab).removeClass('inactive-tab');
	$(newTab).addClass('active-tab');
	$(newDiv).css('display','');
	$('#playlist-name-readout').css('display','');
	$('#playlist-name-input').css('display','none');
	$('#playlist-name-rename').css('visibility','visible');
	$('#playlist-name-readout').html(plist);
}

function newPlaylist(){
	//loadClips();
	oldTab = '#view-tab';
	newTab = '#edit-tab';
	oldDiv = '#playlist-view'
	newDiv = '#edit-view'
	$(oldTab).removeClass('active-tab');
	$(oldTab).addClass('inactive-tab');
	$(oldDiv).css('display','none')
	$(newTab).removeClass('inactive-tab');
	$(newTab).addClass('active-tab');
	$(newDiv).css('display','');
	$('#playlist-name-readout').css('display','none');
	$('#playlist-name-input').css('display','');
	$('#playlist-name-rename').css('visibility','hidden');
	loadClips;
}

function editClip(clip){
	if(clip){
		$('#clips-view').css('display','none');
		$('#clips-edit-view').css('display','');
		$('#new-clip-name').val("");
		$('#new-clip-ribbon').val("");
		$('#new-clip-concierge').val("");
		var markers = clipList[clip].split(':');
		$('#new-clip-name').val(clip);
		$('#new-clip-ribbon').val(markers[0]);
		$('#new-clip-concierge').val(markers[1]);
		$('#new-clip-name-label').html("Current Name: " + clip);
		$('#new-clip-ribbon-label').html("Current Ribbon Marker: " + markers[0]);
		$('#new-clip-concierge-label').html("Current Concierge Marker: " + markers[1]);
		editedClip = clip;
	/*
	}
	if(b == "true"){
		$('#clips-view').css('display','none');
		$('#clips-edit-view').css('display','');
		$('#new-clip-name').val("");
		$('#new-clip-ribbon').val("");
		$('#new-clip-concierge').val("");
	*/
	} else {
		loadClips();
		$('#clips-view').css('display','');
		$('#clips-edit-view').css('display','none')
	}
}

function addClip(){
	$('#clips-view').css('display','none');
	$('#clips-edit-view').css('display','');
	$('#new-clip-name').val("");
	$('#new-clip-ribbon').val("");
	$('#new-clip-concierge').val("");
	$('#new-clip-name-label').html("Enter New Name");
	$('#new-clip-ribbon-label').html("Enter New Ribbon Marker");
	$('#new-clip-concierge-label').html("Enter New Concierge Marker");
	loadClips();
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
	var edit = "false";
	if(bEditingClip){
		edit = "true";
	}
	$.ajax({
		url:'clips',
		type:'POST',
		data:{clipName:clipName,ribbonCue:ribbonCue,conciergeCue:conciergeCue,editedClip:editedClip},
		success:function(data){
			loadClips();
			editClip();
		}
	});
}

function loadClips(){
	$.ajax({
		url:'getclips',
		type:'GET',
		success:function(data){
			//alert(data);
			clipList = JSON.parse(data);
			var cueHTML = "";
			//alert(clipList);
			var dd = document.getElementById("cue-dropdown");
			for(var key in clipList){
				//alert(key);
				if(dd){
					dd.options.add(new Option(key, key));
				}
				var markers = clipList[key].split(":");
				cueHTML += "<b>" + key + "</b>" + "<div class='bottom-bordered'><span style='float:right;'><img src='static/img/edit.png' onclick='editClip(\"" + key + "\")'></img></span><br>" +
				"<span style='margin-left:10px;'><b>Ribbon: </b>" + markers[0] + "</span><br>" +
				"<span style='margin-left:10px;'><b>Concierge: </b>" + markers[1] + "</span><br><br></div>";
			}
			$('#view-clips').html(cueHTML);
		}
	})
}

function loadDropdown(){
	//loadClips();
	//alert("loading dropdown.")
	//var dd = document.getElementById("cue-dropdown");
	//for(var key in clipList){
	//	alert("dd:" + key)
	//	dd.options.add(new Option(key, key))
	//}	
	//alert("dropdown loaded.")
	var dd = document.getElementById("cue-dropdown");
	for(var key in clipList){
		if(dd){
			//alert(key);
			dd.options.add(new Option(key, key));
		}
	}
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
	if(cue != "__IGNORE__"){
		currentPlaylist.push(cue);
		populatePlaylist();
	}
}

function insertCue(cue){
	var cueDropdown = document.getElementById("cue-dropdown");
	var cue = cueDropdown.options[cueDropdown.selectedIndex].value;
	if(cue != "__IGNORE__"){
		currentPlaylist.splice(parseInt(highlightedCue) + 1, 0, cue);
		currentPlaylist.join();
		deactivateHighlight();
		populatePlaylist();
	}
}

function removeCue(cue){
	var cueIndex = parseInt(cue);
	currentPlaylist.splice(cueIndex,1);
	deactivateHighlight();
	populatePlaylist();
} 

function populatePlaylist(){
	var playlistHTML = ''
	for(var i = 0; i < currentPlaylist.length; i++){
		var cueIndex = i.toString();
		var cueId = "cue-" + cueIndex;
		playlistHTML += "<div style='padding-top:10px; padding-bottom:20px; border-bottom:1px solid #b9b8bb;'><span style='padding-top:5px;' onclick='toggleHighlight(" + i + ")' id='" + cueId + "' class='cue-item'>" + currentPlaylist[i] + 
		"</span><span onclick='removeCue(" + cueIndex + ")' class='cue-remove'><img style='float: right;' src='static/img/remove.png'></img></span><br></div>"	;
	}
	$('#playlist-creator').html(playlistHTML);

}

function activateRenamePlaylist(){
	var name = $('#playlist-name-readout').html();
	//alert("changing name of " + name);
	$('#playlist-name-readout').css('display','none');
	$('#playlist-name-input').css('display','');
	$('#playlist-name-rename').css('visibility','hidden');
	bRename = true;
}

function savePlaylist(){
	//alert("saving playlist.");
	if(bRename){
		oldPlaylistName = currentPlaylistName;
		currentPlaylistName = document.getElementById('new-playlist-name').val();
		//alert(currentPlaylistName);
	} else {
		currentPlaylistName = $('#new-playlist-name').val();
	}
	if(currentPlaylistName == ""){
		alert("Please enter a name for the playlist.");
		return;
	}
	var playlistStr = "";
	for(var i in currentPlaylist){
		playlistStr += currentPlaylist[i] + ":";
	}
	$.ajax({
		url:'playlists',
		type:'POST',
		data:{name:currentPlaylistName,playlist:playlistStr}
	});
}

function cancelEdit(){
	swapPlaylistTab('view');
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