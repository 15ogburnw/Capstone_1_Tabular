const $searchForm = $("#search-form");

const $searchBtn = $("#search-button");

const $searchInput = $("#search-input");

$searchBtn.on("click", (e) => {
  $searchForm.submit();
});

$searchForm.on("submit", function (event) {
  event.preventDefault();
  handleSubmit();
});

async function handleSubmit() {
  const query = $searchInput.val();
  const response = await axios.get("/api/songs", { params: { query: query } });

  showResults(response.data);
}

function showResults(songs) {
  const $resultsList = $("#results-list");

  $resultsList.empty();

  let html;
  songs = JSON.parse(songs);

  for (let song of songs) {
    console.log(song);
    html = getSongHTML(song);

    $resultsList.append(html);
  }
}

function getSongHTML(song) {
  const $newLI = $("<li>");
  const $anchor = $("<a>");
  $anchor.attr("data-song-id", song.id);
  $anchor.attr("href", `https://www.songsterr.com/a/wa/song?id=${song.id}`);
  $anchor.append(`${song.title} by ${song.artist.name}`);
  const html = $newLI.append($anchor);

  return html;
}
