const BASE_URL = "http://localhost:5000";

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

$("#addToPlaylist").on("show.bs.modal", function (event) {
  const $button = $(event.relatedTarget);
  console.log($button);
  const songInfo = $button.data("song-info");
  console.log(songInfo);
  $("#add-song").data("song-info", songInfo);
  const $modal = $(this);
  $modal.find(".modal-title").text(songInfo.title + " by " + songInfo.artist);
});

$("#add-song").on("click", function () {
  const songInfo = $(this).data("song-info");
  $("#playlists-form").trigger("submit", songInfo);
});

$("#playlists-form").on("submit", async function (e, songInfo) {
  e.preventDefault();
  const playlists = [];
  $('input[name="playlist-box"]:checked').each(function () {
    playlists.push(JSON.parse(this.value));
  });
  const json = {
    songInfo: songInfo,
    playlists: playlists,
  };

  const resp = await axios.post(`${BASE_URL}/playlists/add-song`, {
    json: JSON.stringify(json),
  });

  $("#addToPlaylist").modal("hide");
  $('input[name="playlist-box"]').each(function () {
    $(this).prop("checked", false);
  });
});
