$(document).ready(function(){

  var change_flag = false;

  var set_rating = function(value){
    for (var i=1; i<=value; ++i){
      $(".star-"+i).css('background-position-x', '-20px');
    }
    for (var i=value+1; i<=5; ++i){
      $(".star-"+i).css('background-position-x', '');
    }

    $("#radio"+value).prop("checked", true);
  };

  var request_prediction = function(){
     var entry = $('.review-box').val();
    $.ajax({
      type:"POST",
      url:"rate/predict",
      data:{
        'text': entry
      },
      success: function(data){
        set_rating(data.value);
      }
    }); 
  };

  var timer = setInterval(function(){
    if(change_flag){
      request_prediction();
      change_flag = false;
    }
  }, 500);
  request_prediction();

  $('.review-box').keydown(function(event){
    change_flag = true; 
  });

});
