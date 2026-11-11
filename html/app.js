const parameters = new URLSearchParams(window.location.search);

if (parameters.has("png")) {
  document.documentElement.classList.add("png-export");
}
