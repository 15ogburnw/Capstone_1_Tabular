$(document).ready(function () {
  const BASE_URL = window.location.protocol + "//" + window.location.host;

  // Event handler for when the modal is triggered
  $("#addToPlaylist").on("show.bs.modal", async function (event) {
    const $button = $(event.relatedTarget);
    const songInfo = $button.data("song-info");
    $("#add-song").data("song-info", songInfo);

    // Get array of playlist IDs for playlists that contain this song from the API
    const playlistIds = await getPlaylists(songInfo.id);

    // Set title of modal to title and artist of song
    const $modal = $(this);
    $modal.find(".modal-title").text(songInfo.title + " by " + songInfo.artist);

    // Get array of playlist checkboxes from the modal
    const $playlists = $(".form-check");
    let playlistId;

    // Loop through array of playlist checkboxes
    for (let playlist of $playlists) {
      playlist.hidden = false;
      // Get the playlist ID from the value of the checkbox
      playlistId = JSON.parse(
        $(playlist).find(".form-check-input").eq(0).val()
      ).id;

      // If the ID is present in the array of IDs retrieved from the API, hide it
      if (playlistIds.includes(playlistId)) {
        playlist.hidden = true;
      }
    }
  });

  // Event handler for when the modal is hidden
  $("#addToPlaylist").on("hide.bs.modal", function () {
    //Uncheck all checkboxes when the modal is hidden
    $('input[name="playlist-box"]').each(function () {
      $(this).prop("checked", false);
    });
  });

  // Trigger submission of modal form of checkboxes; pass the submit function a songInfo object
  // for the current song
  $("#add-song").on("click", function () {
    const songInfo = $(this).data("song-info");
    $("#playlists-form").trigger("submit", songInfo);
  });

  // submission handling
  $("#playlists-form").on("submit", async function (e, songInfo) {
    e.preventDefault();
    const playlists = [];

    // create an array containing info about each playlist that was checked
    $('input[name="playlist-box"]:checked').each(function () {
      playlists.push(JSON.parse(this.value));
    });

    // create a JSON object with info about the song and all playlists that it will be added to
    const json = JSON.stringify({
      songInfo: songInfo,
      playlists: playlists,
    });

    // Send a post request to the add song endpoint including the JSON object as data
    const resp = await axios.post(`${BASE_URL}/playlists/add-song`, {
      json: json,
    });

    // Hide the modal and uncheck all checkboxes
    $("#addToPlaylist").modal("hide");
    $('input[name="playlist-box"]').each(function () {
      $(this).prop("checked", false);
    });
  });

  // Click handling for removing a song from a playlist
  $(".remove-song").on("click", async function (e) {
    e.preventDefault();
    songInfo = $(this).data("song-info");
    playlistId = $(this).data("playlist-id");

    // Create a JSON object with info about the song
    const json = JSON.stringify(songInfo);

    // Send a post request to remove the song, passing in the song info
    const resp = await axios.post(
      `${BASE_URL}/playlists/${playlistId}/remove-song`,
      {
        json: json,
      }
    );

    // Remove the song from the DOM
    $(this).closest("tr").remove();

    // If there are no songs remaining on the DOM, append a message above the songs list
    if ($("#songs-list").find("tbody").children().length < 1) {
      $("<h5>There are no songs in this playlist!</h5>").insertBefore(
        $("#songs-list")
      );
      $("table").hide();
    }
  });

  // Get an array of playlist IDs for all playlists that a song is in, given a song ID
  async function getPlaylists(songId) {
    resp = await axios.get(`${BASE_URL}/api/songs/${songId}/playlists`);
    return resp.data;
  }
});

// Generate a button to trigger the Add Song modal for each song, containing a data attribute
// with info about the song
function getModalBtn(song) {
  const songInfo = {
    id: song.id,
    title: song.title,
    artist: song.artist.name,
    tab_url: `https://www.songsterr.com/a/wa/song?id=${song.id}`,
  };

  const $btn = $("<button>");
  $btn
    .attr({
      type: "button",
      class: "btn btn-primary",
      "data-toggle": "modal",
      "data-target": "#addToPlaylist",
      "data-song-info": JSON.stringify(songInfo),
    })
    .append("Add Song to Playlist");

  return $btn;
}
