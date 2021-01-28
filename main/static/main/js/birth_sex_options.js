let sex = $("#id_sex_assigned_at_birth");
let explain_box = $("#explain_box");
let weeks_pregnant = $("#id_weeks_pregnant");

sex.on("change", () => {
  if (sex.val() == "m") {
    explain_box.css("visibility", "hidden");
    explain_box.css("display", "none");
    weeks_pregnant.prop("disabled", true);
  } else if (sex.val() == "f") {
    explain_box.css("visibility", "hidden");
    explain_box.css("display", "none");
    weeks_pregnant.prop("disabled", false);
  } else if (sex.val() == "o") {
    explain_box.css("visibility", "visible");
    explain_box.css("display", "block");
  }
});
