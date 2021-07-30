$("#id_phone_number").inputmask({ regex: "^\+(?:[0-9] ?){6,14}[0-9]$" });

let social = $("#id_social_security_number");

social.inputmask({ mask: "[999-99-]9999" });

let zip_code = $("#id_zip_code");

zip_code.inputmask({ mask: "99999[-9999]" });

function reformat_social() {}

social.bind("keydown keyup mousedown mouseup", reformat_social);

function reformat_float() {
  console.log("Reformatting secondary height.");
  secondary_height.val(parseFloat(secondary_height.val()).toFixed(2));
}

let secondary_height = $("id_body_height_secondary");
secondary_height.bind("keyup mouseup", reformat_float);
