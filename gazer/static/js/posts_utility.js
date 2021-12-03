function resizeThumbs(){
  var size = document.getElementById("thumb-size-select").value;
  var allThumbs = document.images;
  for(var i = 0; i < allThumbs.length; i++){
    if(allThumbs[i].classList.contains("post")){
      allThumbs[i].width = size;
    }
  }
}

async function tagComplete(value){
  let response = await fetch("/tagcomplete/" + value);
  let optionList = "";

  if (response.ok) {
    let json = await response.json();
    for(var i = 0; i <  json.length; i++ ){
      optionList += `<option value="${json[i]}"></option>\n`;
    }
    return optionList;

  } else {
    console.error("http error: " + response.status);
  }

  return ""
}


