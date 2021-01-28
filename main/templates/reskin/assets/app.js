(function ($) {
  $(function () {
    $("input, textarea").placeholder();

    $(".date-picker").datepicker({
      uiLibrary: "bootstrap4",
    });

    $("input[type='number']").inputSpinner();

    jQuery.validator.setDefaults({
      debug: true,
      success: "valid",
      ignore: [".ignoreThisClass"],
      highlight: function (element) {
        jQuery(element).closest(".form-control").addClass("is-invalid");
      },
      unhighlight: function (element) {
        jQuery(element).closest(".form-control").removeClass("is-invalid");
      },
      errorElement: "span",
      errorClass: "label label-danger",
      errorPlacement: function (error, element) {
        if (element.parent(".input-group").length) {
          error.insertAfter(element.parent());
        } else {
          error.insertAfter(element);
        }
      },
    });

    var formSettings = {
      rules: {
        inputDate1: {
          required: true,
          // step: 10
        },
        inputText3: "required",
        weight: "required",
      },
      messages: {
        weight: {
          required: "", /* Present only icon (!) */
        },
      },
    };

    $("form#add-patient").validate(formSettings);

    $('#modal-loading').on('show.bs.modal', function (e) {
      var modal = $(this)
      console.log(modal);
      setTimeout(function(){
        
        modal.modal('hide')
        
        $('#message-error').collapse('toggle')

      }, 3000);
    });

  });
})(jQuery);
