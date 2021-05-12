function calculate_bmi(body_height, body_weight) {
  return (body_weight / (body_height * body_height)).toFixed(1);
}

function get_input_and_calc() {
  let body_height =
    parseInt($("#id_form-body_height_primary").val()) +
    (parseInt($("#id_form-body_height_secondary").val()) / 100);
  let body_weight = $("#id_form-body_weight").val();
  return calculate_bmi(body_height, body_weight);
}

function set_final_value() {
  console.log("Metric BMI compuation.");
  $("#id_form-body_mass_index").val(get_input_and_calc);
}

$("#id_form-body_height_primary").on("change", set_final_value);
$("#id_form-body_height_secondary").on("change", set_final_value);
$("#id_form-body_weight").on("change", set_final_value);
