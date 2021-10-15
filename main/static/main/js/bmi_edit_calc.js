function calculate_bmi(body_height, body_weight) {
  return ((body_weight / (body_height * body_height)) * 703).toFixed(1);
}

function get_input_and_calc() {
  let body_height =
    parseInt($("#id_body_height_primary").val()) * 12 +
    parseInt($("#id_body_height_secondary").val());
  let body_weight = $("#id_body_weight").val();
  return calculate_bmi(body_height, body_weight);
}

function set_final_value() {
  console.log("Imperial BMI computation.");
  $("#id_body_mass_index").val(get_input_and_calc);
}

$("#id_body_height_primary").on("change", set_final_value);
$("#id_body_height_secondary").on("change", set_final_value);
$("#id_body_weight").on("change", set_final_value);
