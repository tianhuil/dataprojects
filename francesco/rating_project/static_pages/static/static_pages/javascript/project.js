$(document).ready(function(){

  $('.code-toggle').click(function(){
    $(this).toggleClass('.code-toggle-on');
    $('div.input.hbox').toggle();
  });

});
