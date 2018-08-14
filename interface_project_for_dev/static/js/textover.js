window.onload = function(){
	var td = document.getElementsByTagName('td');
	if(td.length<0) return;
	for (var i = 0,len = td.length - 1; i < len; i++) {
		var text = td[i].innerText;
		subStr(td[i],text,25)
	}
}

function subStr(tag,text,num){
	if(text.toString().length > num){
		var newText = text.substr(0,num);
		tag.innerText = newText;
		tag.setAttribute('title',text);
	}
}