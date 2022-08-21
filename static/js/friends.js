$(document).ready(function () {
  const BASE_URL = "http://localhost:5000";

  $("#friend-request").on("click", async function (e) {
    const userID = $(this).data("user-id");
    const resp = await axios.post(`${BASE_URL}/users/request-friend/${userID}`);

    $(this).remove();
    const $success = $("<div>")
      .addClass("alert alert-success")
      .append("Friend request sent!");
    $(".button-container").append($success);
  });

  $("#notifications").on("click", ".accept-friend", async function (e) {
    const userID = $(this).data("user-id");
    const $success = $("<div>")
      .addClass("alert alert-success")
      .append("Success! You are now friends!");
    const resp = await axios.post(`${BASE_URL}/users/accept-request/${userID}`);

    $(this).parent().empty().append($success);
  });

  $("#notifications").on("click", ".deny-friend", async function (e) {
    const userID = $(this).data("user-id");

    const resp = await axios.post(`${BASE_URL}/users/deny-request/${userID}`);

    $(this).parent().empty();
  });
});
