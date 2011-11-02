/**
 * CHANGES
 * v.2.1.3 - Made it $.noConflict() compatible
 * v.2.1.2 - Fixed bug in which nested fieldsets do not work correctly.
 * v.2.1.1 - Forgot to put the new filter from v.2.1 into the if (settings.closed)
 * v.2.1 - Changed jQuery(this).parent().children().filter( ELEMENTS HERE) to jQuery(this).parent().children().not('label').  Prevents you from having to guess what elements will be in the fieldset.
 * v.2.0 - Added settings to allow a fieldset to be initiated as closed.
 *
 * This script may be used by anyone, but please link back to me.
 *
 * Copyright 2009-2010.  Michael Irwin (http://michael.theirwinfamily.net)
 * 
 * -----------------------------------------------------------------------------
 * Changes by Samuele Santi, 2011-11-02
 * - Added .collapse_open() and .collapse_close() methods to manually
 * 	 toggle state.
 * - Added "speed" option to .collapse(), in order to choose animation speed.
 * - Fieldsets with "start-collapsed" class are automatically collapsed
 *   at start.
 * -----------------------------------------------------------------------------
 */
       
jQuery.fn.collapse = function(options) {
	var defaults = {
		closed : false,
		speed : 'fast',
	}
	settings = jQuery.extend({}, defaults, options);

	return this.each(function() {
		var obj = jQuery(this);
		
		obj.find("legend:first")
			.addClass('collapsible')
			.click(function() {
				if (obj.hasClass('collapsed')) {
					obj.removeClass('collapsed').addClass('collapsible');
				}
				jQuery(this).removeClass('collapsed');
				obj.children().not('legend').toggle(settings.speed, function() {
				 
					 if (jQuery(this).is(":visible"))
						obj.find("legend:first").addClass('collapsible');
					 else
						obj.addClass('collapsed').find("legend").addClass('collapsed');
				 });
			})
			.prepend('<span class="collapse-indicator">&nbsp;</span>');
		
		//obj.find("legend:first").prepend('<span class="collapse-indicator">&nbsp;</span>');
		
		if (settings.closed || obj.hasClass('start-collapsed')) {
			obj.addClass('collapsed').find("legend:first").addClass('collapsed');
			obj.children().not("legend:first").css('display', 'none');
		}
	});
	//$("legend.collapsible").prepend('<span class="collapse-indicator">&nbsp;</span>');
};

jQuery.fn.collapse_close = function(options) {
	var defaults = {
		speed : 'fast',
	}
	settings = jQuery.extend({}, defaults, options);

	return this.each(function() {
		var obj = jQuery(this);
		obj.addClass('collapsed').find("legend:first").addClass('collapsed');
		obj.children().not("legend:first").css('display', 'none');
	});
}

jQuery.fn.collapse_open = function(options) {
	var defaults = {
		speed : 'fast',
	}
	settings = jQuery.extend({}, defaults, options);

	var obj = jQuery(this);
	obj.removeClass('collapsed').addClass('collapsible');
	jQuery(this).removeClass('collapsed');

	obj.children().not('legend').toggle(settings.speed, function() {
		 if (jQuery(this).is(":visible")) {
			obj.find("legend:first").addClass('collapsible');
		 }
		 else {
			obj.addClass('collapsed').find("legend").addClass('collapsed');
		 }
	 });
}
