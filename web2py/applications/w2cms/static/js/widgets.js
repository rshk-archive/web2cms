$(document).ready(function() {

//===========================================================
// Collapse "collapsible" <fieldset>s
//===========================================================
$("fieldset.collapsible").collapse({'speed':'fast'});

//===========================================================
// Add "blank" button right of datetime fields and other
// inputs with the 'blankable' class.
//===========================================================
$('input.datetime,input.blankable').each(function(){
	oc = "$('#"+this.id+"').val('');return false;"
	$(this).after('<button class="blank-btn" onclick="'+oc+'">BLANK</button>');
});

});
