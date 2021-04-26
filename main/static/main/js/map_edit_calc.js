function calculate_map(systolic, diastolic) {
    return ((1 / 3) * systolic + (2 / 3) * diastolic).toFixed(1);
}

function get_map_input_and_calc() {
    let systolic = $("#id_systolic_blood_pressure").val();
    let diastolic = $("#id_diastolic_blood_pressure").val();
    return calculate_map(systolic, diastolic);
}

function set_final_map_value() {
    $("#id_mean_arterial_pressure").val(get_map_input_and_calc);
}

$("#id_diastolic_blood_pressure").on("change", set_final_map_value);
$("#id_systolic_blood_pressure").on("change", set_final_map_value);
