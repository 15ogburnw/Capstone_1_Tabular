const $searchForm = $("#search-form");
const $searchBtn = $("#search-button");
const $searchInput = $("#search-input");
const $resultsList = $("#results-list");

$searchBtn.on("click", (e) => {
  $searchForm.submit();
});

$searchForm.on("submit", function (event) {
  event.preventDefault();
  handleSubmit();
});

async function handleSubmit() {
  const query = $searchInput.val();
  const response = await axios.get(
    `https://www.songsterr.com/a/ra/songs.json?pattern=${query}`
  );

  showResults(response.data);
}

async function showResults(songs) {
  $resultsList.empty();
  let html;
  const likes = await getLikedSongs();

  for (let song of songs) {
    if (likes.includes(song.id)) {
      html = getSongHTML(song, true);
    } else {
      html = getSongHTML(song, false);
    }

    $resultsList.append(html);
  }
}

function getSongHTML(song, isLiked) {
  const $newLI = $("<li>");
  const $tabLink = $("<a>");

  const songInfo = {
    id: song.id,
    title: song.title,
    artist: song.artist.name,
    tab_url: `https://www.songsterr.com/a/wa/song?id=${song.id}`,
  };

  $tabLink.attr("href", songInfo.tab_url);
  $tabLink.append(`${song.title} by ${song.artist.name}`);
  $newLI.append($tabLink);

  if (!isLiked) {
    const $like = $("<a href='#'>").append("Like");
    $like
      .attr("data-song-info", JSON.stringify(songInfo))
      .attr("data-is-liked", false)
      .addClass("like");
    const html = $newLI.append($like);
    return html;
  } else {
    const $unlike = $("<a href='#'>").append("Unlike");
    $unlike
      .attr("data-song-info", JSON.stringify(songInfo))
      .attr("data-is-liked", true)
      .addClass("like");
    const html = $newLI.append($unlike);
    return html;
  }
}

async function getLikedSongs() {
  resp = await axios.get("/api/likes");
  return resp.data;
}

$resultsList.on("click", ".like", toggleLike);

async function toggleLike(e) {
  const songInfo = $(this).attr("data-song-info");

  const isLiked = $(this).attr("data-is-liked");
  console.log(isLiked);

  if (isLiked === "false") {
    const resp = await axios.post("http://localhost:5000/users/likes", {
      json: songInfo,
    });
    console.log(resp);
    console.log($(this));
    $(this).empty().append("Unlike").attr("data-is-liked", true);
  } else {
    const resp = await axios.post("http://localhost:5000/users/likes", {
      json: songInfo,
    });
    $(this).empty().append("Like").attr("data-is-liked", false);
  }
}
