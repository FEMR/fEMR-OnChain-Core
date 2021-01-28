const diff_years = (dt2, dt1) => {
  var diffTime = dt2.getTime() - dt1.getTime();
  var daysDiff = diffTime / (1000 * 3600 * 24);
  return Math.floor(Math.abs(daysDiff) / 365);
};

const calculate_age = (date_of_birth) => diff_years(date_of_birth, new Date());

const get_date_of_birth = () => new Date($("#id_date_of_birth").val());

const set_final_value = (date_of_birth) => {
  $("#id_age").val(date_of_birth);
};

$("#id_date_of_birth").on("change", () => {
  set_final_value(calculate_age(get_date_of_birth()));
});
