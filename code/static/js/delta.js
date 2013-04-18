var editorMode = 'name';
var currentPlaylistName = "";
var oldPlaylistName = "";
var currentPlaylist = new Array();
var bRename = false;
var highlightedCue = 0;
var bHaveHighlightedCue = false;
var playlistList = '';
var bHaveOpenPlaylist = false;
var clipList;
var bEditingClip = false;
var editedClip;
var schedulerDate = ""

function init(){
	$.ajax({
		url:'getplaylists',
		type:'POST',
		success: function(data){
			playlistList = eval(data);
		}
	});
	$.ajaxSetup({cache:false});
	//$('.default').dropkick();
	//Cufon.replace('.hp-text');
}

/*
The datepicker used by the scheduler.
*/

function initDatepicker(){
	var today = new Date();
	$(function() {
        $("#datepicker").datepicker({
        	defaultDate: today,
        	//minDate: 0,
        	'setDate': today,
			onSelect: function(date){
				//alert(date)
				schedulerDate = date;
				updateScheduler(date);
			}
		})
	});
	d = today.getDate().toString();
	if(d.length < 2){
		d = "0" + d
	}
	mInt = today.getMonth() + 1;
	m = mInt.toString();
	if(m.length < 2){
		m = "0" + m;
	}
	y = today.getFullYear().toString();
	dateToSet = m + '/' + d + '/' + y;
	schedulerDate = dateToSet;
	updateScheduler(schedulerDate);
}

/*
Post a test message to the server.
*/

function sndMsg(){
	msg = $('#msg-input').val()
	$.ajax({
		url:'sndmsg',
		type:'POST',
		data:{msg:msg},
	})
}

/*
Sync a date on the scheduler UI to the database.
*/

function updateScheduler(date){
	$.ajax({
		url:'submitdate',
		type:'POST',
		data:{date:date,action:'get'},
		success: function(data){
			loadScheduler(data);
		}
	})
}

/*
Clear the scheduler.  Called before setting dates.
*/

function resetScheduler(){
	for(var i = 0; i < 24; i++){
		for(var j = 0; j < 60; j += 15){
			var hourExtra = "";
			var minExtra = "";
			if(i < 10){
				hourExtra = "0";
			}
			if(j < 10){
				minExtra = "0";
			}
			var ddId = "dd-" + hourExtra + i.toString() + "-" + minExtra + j.toString();
			document.getElementById(ddId).value = "";
			//alert("clearing " + ddId);
			//$(ddId).val("none");
		}
	}
}

/*
Load the scheduler slots with their corresponding playlists.
Slots are selected by parsing the time building the div id with them.
*/

function loadScheduler(data){
	var playlists = eval('(' + data + ')');
	resetScheduler(); 
	for(var p in playlists){
		if(playlists.hasOwnProperty(p)){
			var hour = p.split(':')[0];
			var min = p.split(':')[1];
			//if(min == "00"){
			//	min = "0";
			//}
			var ddId = "dd-" + hour + "-" + min;
			var playlist = playlists[p];
			//alert("setting " + ddId + " to " + playlist);
			//$(hour + ' > ' + min).html(playlist);
			//$(ddId).val(playlist);
			document.getElementById(ddId).value = playlist;
		}
	}
}

/*
Get the schedule for a particular date.
*/

function getSchedule(){
	//var date = $('#datepicker').val();
	if(schedulerDate == ""){
		alert("No date selected.");
		return;
	}
	var data = new Object;
	for(var i = 0; i < 24; i++){
		for(var j = 0; j < 60; j += 15){
			var hourExtra = "";
			var minExtra = "";
			if(i < 10){
				hourExtra = "0";
			}
			if(j < 10){
				minExtra = "0";
			}
			var dropdown = "dd-" + hourExtra + i.toString() + "-" + minExtra + j.toString();
			//var dropdownVal = $(dropdown).val();
			var dropdownVal = document.getElementById(dropdown).value;
			//alert(dropdownVal);
			if(dropdownVal != ""){
				//alert(dropdown + " = " + dropdownVal);
				var hour;
				var min;
				if(i < 10){
					hour = "0" + i.toString();
				} else {
					hour = i.toString();
				}
				if(j < 10){
					min = "0" + j.toString();
				} else {
					min = j.toString();
				}
				data[hour + ':' + min] = dropdownVal;
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
	data['date'] = schedulerDate;
	return data;
}

/*
Save the the schedule as configured on the scheduler UI.
*/

function saveSchedule(mode){
	var schedule = getSchedule();
	schedule['action'] = 'set'
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

/*
Setup a playlist div.
*/

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

/*
Send a control command the the server.
*/

function sendCmd(cmdType, command){
	//alert(command + " pressed.");
	$.ajax({
		url:'control',
		type:'POST',
		data:{cmdtype:cmdType,cmd:command}
	});
}

/*
Send a playlist to the server.
*/

function sendPlaylist(){
	var dd = document.getElementById("playlist-dropdown");
	var selectedPlaylist = dd.options[dd.selectedIndex].value;
	//alert(selectedPlaylist + " selected");
	sendCmd('playlist',selectedPlaylist);
}

/*
Swap the playlist tabs.  Only relevant for tabbed design versions.
*/

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

/*
Request a playlist from the server and then use it to
populate a playlist div.
*/

function getPlaylist(plist){
	$.ajax({
		url:'getplaylist',
		type:'POST',
		data:{playlist:plist},
		success:function(data){
			currentPlaylist = JSON.parse(data);
			currentPlaylistName = plist;
			populatePlaylist();
		}
	})
}

/*
Edit a playlist.  Switches views.
*/

function editPlaylist(plist){
	if(plist){
		getPlaylist(plist);
		currentPlaylistName = plist;
		bRename = false;
		oldTab = '#view-tab';
		newTab = '#edit-tab';
		oldDiv = '#playlist-view';
		newDiv = '#edit-view';
		$(oldTab).removeClass('active-tab');
		$(oldTab).addClass('inactive-tab');
		$(oldDiv).css('display','none')
		$(newTab).removeClass('inactive-tab');
		$(newTab).addClass('active-tab');
		$(newDiv).css('display','');
		$('#playlist-name-readout').css('visibility','visible');
		$('#playlist-name-input').css('visibility','hidden');
		//$('#playlist-name-rename').css('visibility','visible');
		$('#playlist-name-readout').html("Current Playlist Name: " + plist);
		$('#playlist-name-rename').css('visibility','visible');
	} else {
		newTab = '#view-tab';
		oldTab = '#edit-tab';
		newDiv = '#playlist-view';
		oldDiv = '#edit-view';
		$(oldTab).removeClass('active-tab');
		$(oldTab).addClass('inactive-tab');
		$(oldDiv).css('display','none')
		$(newTab).removeClass('inactive-tab');
		$(newTab).addClass('active-tab');
		$(newDiv).css('display','');
	}
}

/*
Send a new default playlist to the server.
*/

function makeDefault(plist){
	$.ajax({
		url:'setdefault',
		type:'POST',
		data:{plist:plist},
		success:function(data){
			//loadClips();
			alert(plist + " set as default playlist.");
		}
	});
}

/*
Set the view for creating a new playlist.
*/

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
	$('#new-playlist-name').val('');
	//$('#playlist-name-readout').css('visibility','hidden');
	//$('#playlist-name-input').css('visibility','visible');
	//$('#new-playlist-name').val(currentPlaylistName);
	//bRename = true;
	activateRenamePlaylist();
	//loadClips();
}

/*
Set up the view for editing a cue.
*/

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
		$('#clips-view').css('display','');
		$('#clips-edit-view').css('display','none');
		$('#clips-title').html('<h2 class="page-label"><b>Current Clip Names</b></h2>');
		loadClips();
	}
}

function addClip(b){
	$('#clips-view').css('display','none');
	$('#clips-edit-view').css('display','');
	$('#new-clip-name').val("");
	$('#new-clip-ribbon').val("");
	$('#new-clip-concierge').val("");
	$('#new-clip-name-label').html("Enter New Name");
	$('#new-clip-ribbon-label').html("Enter Ribbon Marker");
	$('#new-clip-concierge-label').html("Enter Concierge Marker");
	$('#clips-title').html('<h2 class="page-label"><b>Add New Clip</b></h2>');
	//loadClips();
}

/*
Retrieve a clip from the view and send it to the server.
*/

function saveClip(){
	var clipName = $.trim($('#new-clip-name').val());
	if(clipName == ''){
		alert("Please enter a name for the clip.");
		return;
	}
	var ribbonCue = $.trim($('#new-clip-ribbon').val());
	if(ribbonCue == ''){
		alert("Please enter a ribbon cue.")
		return;
	}
	var conciergeCue = $.trim($('#new-clip-concierge').val());
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
		data:{clipName:clipName,ribbonCue:ribbonCue,conciergeCue:conciergeCue},
		success:function(data){
			//loadClips();
			editClip();
		}
	});
}

/*
Get all clips from the server and setup the their view.
*/

function loadClips(){
	$.ajax({
		url:'getclips',
		type:'POST',
		success:function(data){
			//alert(data);
			clipList = JSON.parse(data);
			var cueHTML = "";
			//alert(clipList);
			var dd = document.getElementById("cue-dropdown");
			if(dd){
				dd.options.length = 0;
				dd.options.add(new Option("Select Clip", "__IGNORE__"));
			}
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
	if(dd){
		dd.options.length = 0;
		dd.options.add(new Option("Select Clip", "__IGNORE__"));
	}
	for(var key in clipList){
		if(dd){
			//alert(key);
			dd.options.add(new Option(key, key));
		}
	}
}

function swapClipsTab(currentTab){
}

/*
Setup the playlist.
*/

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

/*
Add a cue to the playlist being built.
*/

function addCue(cue){
	var cueDropdown = document.getElementById("cue-dropdown")
	var cue = cueDropdown.options[cueDropdown.selectedIndex].value;
	if(cue != "__IGNORE__"){
		currentPlaylist.push(cue);
		populatePlaylist();
	}
}

/*
Insert a cue into the current playlist.
*/

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

/*
Remove a cue from the playlist.
*/

function removeCue(cue){
	var cueIndex = parseInt(cue);
	currentPlaylist.splice(cueIndex,1);
	deactivateHighlight();
	populatePlaylist();
} 

/*
Build a playlist view from the playlist currently being edited.
*/

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

/*
Setup the playlist rename.
*/

function activateRenamePlaylist(){
	var name = $('#playlist-name-readout').html();
	//alert("changing name of " + name);
	$('#playlist-name-readout').css('visibility','hidden');
	$('#playlist-name-input').css('visibility','visible');
	$('#new-playlist-name').val(currentPlaylistName);
	$('#playlist-name-rename').css('visibility','hidden');
	bRename = true;
}

/*
Send a new playlist to the server.
*/

function savePlaylist(){
	if(bRename){
		oldPlaylistName = currentPlaylistName;
		currentPlaylistName = $.trim($('#new-playlist-name').val());
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
		data:{name:currentPlaylistName,playlist:playlistStr},
		success:function(){
			//editPlaylist();
			window.location.assign('/playlists');
		}
	});
}

function cancelEdit(){
	window.location.assign('/playlists');
	//swapPlaylistTab('view');
}

function deactivateHighlight(){
	var cueId = "#cue-" + highlightedCue;
	$(cueId).removeClass('highlighted');
	bHaveHighlightedCue = false;
	$('#cue-insert').css('display','none');
	$('#cue-add').css('display','');
}

/*
Toggle the highlight on the playlist item.
*/

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