function sendCmd(cmd){
	alert(cmd + " pressed.");
}

function sendPlaylist(){
	var dd = document.getElementById("playlist-dropdown")
	var selectedPlaylist = dd.options[dd.selectedIndex].value
	alert(selectedPlaylist + " selected");
}