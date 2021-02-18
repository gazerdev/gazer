function resizeThumbs(){
  var size = document.getElementById("thumb-size-select").value;
  var allThumbs = document.images;
  for(var i = 0; i < allThumbs.length; i++){
    allThumbs[i].width = size;
  }
}
